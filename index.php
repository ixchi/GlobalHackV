<?php

date_default_timezone_set('America/Chicago');

require __DIR__ . '/vendor/autoload.php';

$klein = new \Klein\Klein();

$klein->respond(function ($request, $response, $service, $app) {
	$loader = new Twig_Loader_Filesystem(__DIR__ . '/templates');
	$twig = new Twig_Environment($loader);

	$service->twig = $twig;

	$app->register('db', function () {
		return new PDO('mysql:host=127.0.0.1;dbname=globalhackv', 'globalhackv', 'globalhack');
	});
});

$klein->respond('GET', '/', function ($request, $response, $service, $app) {
	return $service->twig->render('home.twig');
});

$klein->respond('GET', '/resources', function ($request, $response, $service, $app) {
	return $service->twig->render('resources.twig');
});

$klein->respond('GET', '/averages', function ($request, $response, $service, $app) {
	return $service->twig->render('averages.twig');
});

$klein->respond('GET', '/averages.json', function ($request, $response, $service, $app) {
	$db = $app->db;
	$stmt = $db->prepare('select `Municipali`, `X`, `Y`, avg(`waiting_time`) as `avg`
from citations
inner join locations on citations.court_location = upper(locations.`Municipali`)
where court_location <> \'\'
group by court_location
order by `avg` asc');
	$stmt->execute();

	return $response->json($stmt->fetchAll(PDO::FETCH_ASSOC));
});

$klein->respond('POST', '/search', function ($request, $response, $service, $app) {
	if (!$request->first_name || !$request->last_name) {
		return $response->redirect('/');
	}

	$birthday = "{$request->birth['year']}-{$request->birth['month']}-{$request->birth['day']}";

	$date = strtotime($birthday);

	$db = $app->db;
	$stmt = $db->prepare('SELECT
	violations.citation_number,
	violation_number,
	citation_date,
	first_name,
	last_name,
	date_of_birth,
	defendant_address,
	defendant_city,
	defendant_state,
	drivers_license_number,
	court_date,
	court_location,
	court_address,
	violation_description,
	warrant_status,
	warrant_number,
	status,
	status_date,
	fine_amount,
	court_cost,
	X,
	Y,
	`Municipal Website` AS `website`,
	`Court Clerk Phone Number` AS `phone`,
	`Online Payment System Provider` AS `payment`
FROM
	citations
INNER JOIN
	violations ON
		citations.citation_number = violations.citation_number
INNER JOIN
	locations ON
		court_address = locations.address
JOIN
	munipality ON
		court_location = UPPER(Municipality)
WHERE
	`last_name` LIKE :name AND
	`date_of_birth` = :birthday AND
	(`drivers_license_number` = \'\' OR `drivers_license_number` LIKE :license)
HAVING
	`defendant_city` != \'\' AND
	`defendant_state` != \'\' AND
	`drivers_license_number` != \'\' AND
	`court_address` != \'\' AND
	`defendant_address` != \'\'
ORDER BY
		`status_date` DESC');
	$name = "%{$request->last_name}%";
	$stmt->bindParam(':name', $name);
	$stmt->bindParam(':birthday', date('Y-m-d', $date));
	$license = $request->drivers_license_id;
	$stmt->bindParam(':license', $license);
	$stmt->execute();

	$results = $stmt->fetchAll(PDO::FETCH_ASSOC);

	if (count($results) === 0) {
		return $service->twig->render('noresults.twig', array(
			'first' => $request->first_name,
			'last' => $request->last_name,
			'birthday' => date('Y-m-d', $date),
			'drivers_license_id' => $request->drivers_license_id
		));
	}

	$info = new stdClass();
	foreach ($results as $row) {
		if ($row['status']  == 'FTA WARRANT ISSUED') {
			if (!property_exists($info, 'warrant')) $info->warrant = array();
			$info->warrant[] = array(
				'violation' => $row['violation_number'],
				'citation' => $row['citation_number']
			);
		}

		if ($row['status']  == 'CONT FOR PAYMENT') {
			if (!property_exists($info, 'fine')) $info->fine = array();
			$info->fine[] = array(
				'amount' => $row['fine_amount'],
				'violation' => $row['violation_number'],
				'citation' => $row['citation_number'],
				'violation_description' => $row['violation_description'],
				'fine_amount' => $row['fine_amount'],
				'court_cost' => $row['court_cost']
			);
		}

		if ($row['fine_amount'] != '') {
			if (!property_exists($info, 'fines_owed')) $info->fines_owed = 0;
			if (!property_exists($info, 'fees_owed')) $info->fees_owed = 0;
			$info->fines_owed = ((int) substr($row['fine_amount'], 1)) + $info->fines_owed;
			$info->fees_owed = ((int) substr($row['court_cost'], 1)) + $info->fees_owed;
		}
	}

	return $service->twig->render('search.twig', array(
		'results' => $results,
		'info' => $info
	));
});

$klein->dispatch();
