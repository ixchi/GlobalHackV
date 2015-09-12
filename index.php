<?php

require __DIR__ . '/vendor/autoload.php';

$klein = new \Klein\Klein();

$klein->respond(function ($request, $response, $service, $app) {
	$loader = new Twig_Loader_Filesystem(__DIR__ . '/templates');
	$twig = new Twig_Environment($loader);

	$service->twig = $twig;

	$app->register('db', function () {
		return new PDO('mysql:host=127.0.0.1;dbname=globalhackv', 'root', '');
	});
});

$klein->respond('GET', '/', function ($request, $response, $service, $app) {
	return $service->twig->render('home.twig');
});

$klein->respond('POST', '/search', function ($request, $response, $service, $app) {
	$db = $app->db;
	$stmt = $db->prepare('SELECT * FROM `good_data` WHERE `last_name` LIKE :name AND `date_of_birth` = :birthday');
	$name = "%{$request->last_name}%";
	$stmt->bindParam(':name', $name);
	$stmt->bindParam(':birthday', $request->date_of_birth);
	$stmt->execute();

	$results = $stmt->fetchAll(PDO::FETCH_ASSOC);

	if (count($results) === 0) {
		return $service->twig->render('noresults.twig');
	}

	return $service->twig->render('search.twig', array('results' => $results));
});

$klein->dispatch();
