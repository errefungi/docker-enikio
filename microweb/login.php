</!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css"
        integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
    <title>LOG IN</title>


</head>

<body style="background-image: linear-gradient(to right,
#ffffff,
#ffffff,
#ffffff,
#ffffff,
#ffffff);">
    <div class="d-flex" id="wrapper">
        <div class="container ">
            <div class="row">
                <div class="col-3"></div>
                <div class="col-6 mb-3">
                    <h1 class="text-center mt-5 mb-5">¡BIENVENIDO/A!</h1>
                    <div class="card ">
                        <div class="card-header">
                            <h3 class="text-center">Ingresa tus datos </h3>
                        </div>
                        <div class="card-body">
                            <form action="ingresar.php" method="post">
                                <label><br />Email<br /></label>
                                <input type="email" class="form-control mb-3" name="email">
                                <label><br />Contraseña<br /></label>
                                <input type="password" class="form-control mb-3" name="password">
                                <button class="btn btn-primary" type="submit" style="background-color: #0F843B">Ingresar
                                    <i class="fas fa-sign-in-alt fa-lg" style="color: #FFFFFF;"></i></button>
                            </form>
                        </div>
                    </div>
                </div>
                <div class="col-3"></div>
            </div>
        </div>
    </div>
</body>
