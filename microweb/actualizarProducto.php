<?php
$id = $_POST['id'];
$inventario = $_POST['inventario'];
$url = "http://192.168.100.2:3002/productos/$id";
  
  // Datos que se desean actualizar
  $data = array("inventario" => $inventario);

  $ch = curl_init();

  curl_setopt($ch, CURLOPT_URL, $url);
  curl_setopt($ch, CURLOPT_CUSTOMREQUEST,"PUT");
  curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
  curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));

  $response = curl_exec($ch);
  $error_code = curl_errno($ch);
  $error_msg = curl_error($ch);
  
  curl_close($ch);
  
  if ($error_code !== 0) {
    // Manejar el error adecuadamente
    echo "Error en la solicitud: $error_msg";
  } else {
    // Redireccionar al usuario a una página HTML específica
    header('Location: admin-prod.php');
    exit;
  }
?>