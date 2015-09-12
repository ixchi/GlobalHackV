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

$klein->respond('POST', '/search', function ($request, $response, $service, $app) {
	if (!$request->first_name || !$request->last_name) {
		return $response->redirect('/');
	}

	$birthday = "{$request->birth['year']}-{$request->birth['month']}-{$request->birth['day']}";

	$date = strtotime($birthday);

	$db = $app->db;
	$stmt = $db->prepare('SELECT
		*
	FROM
		`good_data_fixed`
	WHERE
		`last_name` LIKE :name AND
		`date_of_birth` = :birthday AND
		(`drivers_license_number` = \'\' OR `drivers_license_number` LIKE :license)
	ORDER BY
		`status_date` DESC');
	$name = "%{$request->last_name}%";
	$stmt->bindParam(':name', $name);
	$stmt->bindParam(':birthday', date('Y-m-d', $date));
	$stmt->bindParam(':license', $request->drivers_license_id);
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
			$info->warrant[] = $row['citation_number'];
		}

		if ($row['status']  == 'CONT FOR PAYMENT') {
			if (!property_exists($info, 'fine')) $info->fine = array();
			$info->fine[] = array(
				'amount' => $row['fine_amount'],
				'citation' => $row['citation_number']
			);
		}
	}

	return $service->twig->render('search.twig', array(
		'results' => $results,
		'info' => $info
	));
});

$klein->dispatch();
