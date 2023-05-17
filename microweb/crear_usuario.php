<?php
ob_start();
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $cc = $_POST["cc"];
    $nombre = $_POST["nombre"];
    $email = $_POST["email"];
    $password = $_POST["password"];
    $celular = $_POST["celular"];
    $rol = $_POST["rol"];

    $url = "http://usuarios:3001/usuarios/crearusuario";
    $data = array(
        'cc' => $cc,
        'nombre' => $nombre,
        'email' => $email,
        'password' => $password,
        'celular' => $celular,
        'rol' => $rol
    );

    $payload = json_encode($data);

    $curl = curl_init($url);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($curl, CURLOPT_POST, true);
    curl_setopt($curl, CURLOPT_POSTFIELDS, $payload);
    curl_setopt($curl, CURLOPT_HTTPHEADER, array(
        'Content-Type: application/json'
    ));

    $response = curl_exec($curl);
    curl_close($curl);

    if ($response !== false) {
        header("Location: usuariosadmin.php");
    } else {
        // Aquí puedes manejar el caso en que la petición haya sido exitosa
        // Redirige a la página que desees mostrar después de crear el usuario
        echo "Hubo un error";
    }
}
ob_end_flush();
?>
}
