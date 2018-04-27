<?php

// Quote and escape form submitted values
$geoid = db_quote($_GET['geoid']);

// a test query
$query = "SELECT geoid, aswkt(coordinates) as coord FROM CensusTract where geoid=" . $geoid;

$rows = db_select($query);
if($rows === false) {
	$error = db_error();
	// Handle error - inform administrator, log to file, show error page, etc.
	print($error);
}

$coord = $rows[0]['coord'];
print(json_encode(invertPolygon($coord)));

function invertMultiPolygon($multipolygon) {
	return null;
}

function invertPolygon($polygon) {
	$polygon_len = strlen($polygon);
	$polygon = substr($polygon, 0, $polygon_len-2);
	$polygon = substr($polygon, 9);
	
	$polygon_array = array();
	
	$tmp_polygon_array = preg_split('/,/', $polygon);
	foreach ($tmp_polygon_array as $k => $v) {
		$lon_lat = preg_split('/ /', $v);
		$lat_lon = array();
		$lat_lon['lat'] = $lon_lat[1];
		$lat_lon['lng'] = $lon_lat[0];
		array_push($polygon_array, $lat_lon);
		array_push($polygon_array, $lat_lon);
	}
	return $polygon_array;
}

function db_connect() {
	// define connection as a static variable, to avoid connecting more than once
	static $connection;
	
	// try and connect to the database, if a connection has not been established yet
	if(!isset($connection)) {
		// Load configuration as an array. Use the actual location of your configuration file
		$config = parse_ini_file('../../../config/udf_config.ini'); 

		// try to connect to the database
		$connection = mysqli_connect('localhost',$config['username'],$config['password'],$config['dbname']);
	}
	
	// if connection was not successful, handle the error
	if($connection === false) {
		// handle error - notify administrator, log to a file, show an error on screen, etc.
		return mysqli_connect_error();
	}
	return $connection;
}

function db_query($query) {
	// initiate $result variable
	$result;
	
	// connect to the database
	$connection = db_connect();
	
	// query the database
	$result = mysqli_query($connection, $query);
	
	return $result;
}

function db_select($query) {
	$rows = array();
	$result = db_query($query);

	// If query failed, return `false`
	if($result === false) {
		return false;
	}

	// If query was successful, retrieve all the rows into an array
	while ($row = mysqli_fetch_assoc($result)) {
		$rows[] = $row;
	}
	return $rows;
}


function db_quote($value) {
	$connection = db_connect();
	return "'" . mysqli_real_escape_string($connection,$value) . "'";
}


function db_error() {
	$connection = db_connect();
	return mysqli_error($connection);
}

?>