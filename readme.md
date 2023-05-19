# Proyecto Enikio

Este proyecto implementa una solución para analizar y presentar información de apartamentos y universidades utilizando Docker, Apache Spark, y MySQL en un entorno de Ubuntu 22.04 virtualizado con Vagrant y VirtualBox.

## Herramientas requeridas

- Vagrant
- VirtualBox
- Docker
- Apache Spark

## Implementación

### Configuración de Vagrant

1. Configure una máquina virtual de Ubuntu 22.04 utilizando Vagrant. El siguiente `Vagrantfile` proporciona una configuración básica.

```ruby
Vagrant.configure("2") do |config|
  if Vagrant.has_plugin? "vagrant-vbguest"
    config.vbguest.no_install = true
    config.vbguest.auto_update = false
    config.vbguest.no_remote = true
  end
  config.vm.define :servidorUbuntu do |servidorUbuntu|
    servidorUbuntu.vm.box = "bento/ubuntu-22.04"
    servidorUbuntu.vm.network :private_network, ip: "192.168.100.2"
    servidorUbuntu.vm.hostname = "servidorUbuntu"
    servidorUbuntu.vm.box_download_insecure=true
    servidorUbuntu.vm.provider "virtualbox" do |v|
      v.cpus = 3
      v.memory = 2048
    end
  end
end
```

### Clonación del repositorio e instalación de dependencias

2. Clone el repositorio del proyecto Enikio.

```bash
git clone https://github.com/errefungi/docker-enikio
```
2.1. Cambiar la dirección de ingresar.php por la dirección de la maquina del `Vagrantfile`

```php
header("Location: http://192.168.100.2/admin.php")
// Y
header("Location: http://192.168.100.2/arrendador.php");
```

2.2. Instalación de Apache Spark

Instalar Java
```bash
$ sudo apt update
$ sudo apt install -y openjdk-18-jdk
$ cat <<EOF | sudo tee /etc/profile.d/jdk18.sh
export JAVA_HOME=/usr/lib/jvm/java-1.18.0-openjdk-amd64
export PATH=\$PATH:\$JAVA_HOME/bin
EOF
```
----
```bash
$ source /etc/profile.d/jdk18.sh
```
verificar la instalación obteniendo la versión:
```bash
$ java -version
```
Descargar y descomprimir Spark
Tomar la última versión de spark de https://dlcdn.apache.org/spark/
```bash
$ mkdir labSpark
$ cd labSpark/
$ wget https://dlcdn.apache.org/spark/spark3.4.0/spark-3.4.0-bin-hadoop3.tgz
$tar -xvzf spark-3.4.0-bin-hadoop3.tgz
```
### Creación de la imagen Docker de MySQL

3. Cree la imagen Docker para MySQL versión 5.7.

```bash
sudo docker pull mysql/mysql-server:5.7
```

### Implementación de Docker Compose

4. Navegue hasta el directorio del proyecto docker-enikio y ejecute Docker Compose.

```bash
cd docker-enikio
sudo docker compose up
```

### Implementación de Apache Spark

5. Si desea ejecutar la parte de Apache Spark, siga los siguientes pasos:

   i. En su directorio de trabajo, cree un nuevo archivo `.py` y copie el código de la aplicación Spark proporcionado en el repositorio.

   ii. Instale Spark en su máquina.

   iii. Ejecute desde el directorio `sbin` los comandos `./start-master.sh` y `./start-worker.sh {ip master spark}` 

   iv. Ejecute la aplicación Spark desde el directorio `bin` con el siguiente comando:

```bash
./spark-submit --master spark://192.168.100.3:7077 --conf spark.executor.memory=2g /root/enikiofolder/proyecto-redes/enikiospark.py "/root/enikiofolder/proyecto-redes/db/data" 2> errores.tmp | tee salida.tmp && echo "La app se ejecutó con éxito" || echo "La app falló"
```

Esta secuencia de comandos generará archivos CSV que se pueden utilizar para fines de análisis.

---
