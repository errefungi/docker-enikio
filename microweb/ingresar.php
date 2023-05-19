<?php
ob_start();
$user = $_POST["email"];
$pass = $_POST["password"];
$servurl = "http://usuarios:3001/usuarios/$user/$pass";
$curl = curl_init($servurl);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($curl);
curl_close($curl);

if ($response === false) {
    header("HTTP/1.1 500 Internal Server Error");
    //echo "No hay nada en la response";
}

$resp = json_decode($response);

if (isset($resp) && (is_array($resp) || is_object($resp)) && count($resp) != 0) {
    session_start();
    $dec = $resp[0];
    $nombre = $dec->nombre;
    $rol = trim($dec->rol); //trim quita espacios al final y al inicio
    $cc = $dec->cc;
    $_SESSION["usuario"] = $user;
    $_SESSION["rol"] = $rol;
    $_SESSION["cc"] = $cc;
    $_SESSION["nombre"] = $nombre;
    if ($rol == "arrendador") {
        //header("Access-Control-Allow-Origin: http://192.168.100.9/arrendador.php"); // Reemplaza "http://tu-sitio-web.com" por tu dominio
        //header("Content-Type: application/json");
	header("Location:arrendador.php");
	//echo $rol."hola";
	//echo '<script type="text/javascript"> window.location = "http://192.168.100.9/arrendador.php" </script>';
	//echo json_encode(["result" => "arrendador"]);
        exit;
    } else if ($rol == "admin") {
        //header("Access-Control-Allow-Origin: http://192.168.100.9/admin.php"); // Reemplaza "http://tu-sitio-web.com" por tu dominio
        //header("Content-Type: application/json");
	// echo $rol."hola";
	 //echo '<script type="text/javascript"> window.location = "http://192.168.100.9/admin.php" </script>';
	header("Location:admin.php");
	//echo json_encode(["result" => "admin"]);
        exit;
    }
} else {
    header("HTTP/1.1 401 Unauthorized");
    echo $response;
    echo "response fallida";
}
//ob_end_flush();
?>

