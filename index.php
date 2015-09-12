<?php

require __DIR__ . '/vendor/autoload.php';

$klein = new \Klein\Klein();

$klein->respond('GET', '/', function ($request, $response, $service, $app) {
	return 'Hello, world!';
});

$klein->respond('POST', '/search', function ($request, $response, $service, $app) {
	return 'You made a search, nice.';
});

$klein->dispatch();
