import requests
from pyspark.sql.functions import udf, col, lit, least, when, avg
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType, StringType
from math import radians, sin, cos, sqrt, atan2
from pyspark.sql import SparkSession
import json

spark = SparkSession.builder.appName("Enikio EDA").getOrCreate()

#Funcion para calcular la distancia entre dos puntos de una esfera
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  #Radio de la tierra
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)

def nearest_university(*distances):
    university_names = ["_".join(name.split("_")[2:]) for name in distance_columns]
    min_distance_index = distances.index(min(distances))
    return university_names[min_distance_index]


# un UDF es una función definida por el usuario que se puede aplicar a columnas en un DataFrame.
haversine_udf = udf(haversine, FloatType())
nearest_university_udf = udf(nearest_university, StringType())

#Realizando la carga de los dataframes 
response_postu = requests.get("http://192.168.100.3:3003/postu")
response_aptos = requests.get("http://192.168.100.3:3002/apartamentos")
response_uni = requests.get("http://192.168.100.3:3002/universidades")

# CONVERTIMOS LA RESPUESTA A FORMATO JSON
data_postu = json.loads(response_postu.text)
data_aptos = json.loads(response_aptos.text)
data_uni = json.loads(response_uni.text)

# Convertir el objeto JSON en una lista de strings JSON
jsonStrings_postu = [json.dumps(record) for record in data_postu]
jsonStrings_aptos = [json.dumps(record) for record in data_aptos]
jsonStrings_uni = [json.dumps(record) for record in data_uni]

# Leer los datos JSON en un DataFrame
postulacionesDF = spark.read.json(spark.sparkContext.parallelize(jsonStrings_postu))
aptosDF = spark.read.json(spark.sparkContext.parallelize(jsonStrings_aptos))
uniDF = spark.read.json(spark.sparkContext.parallelize(jsonStrings_uni))

# OBTENER COORDENADAS POR SEPARADO
# MODIFICANDO LOS DATASETS PARA OBTENER LOS DATOS DE LOCALIZACIÓN
uniDF = uniDF.withColumn("lat", col("coord.x").cast("float"))
uniDF = uniDF.withColumn("lon", col("coord.y").cast("float"))
aptosDF = aptosDF.withColumn("lat", col("coord.x").cast("float"))
aptosDF = aptosDF.withColumn("lon", col("coord.y").cast("float"))

# Seleccionar solo las columnas que necesitas
postulacionesDF = postulacionesDF.select("id_apto", "cc_postulado", "fecha", "ocupacion", "interes", "estado")
aptosDF = aptosDF.select("link", "id_apto", "precio", "cant_h", "coord", "hab_disponibles", "id_arrendador", "lat", "lon")
uniDF = uniDF.select("nombre", "coord","lat", "lon")
ocupacionCount = postulacionesDF.groupBy("ocupacion").count()

# Comparar la distancia a cada universidad
for row in uniDF.collect():
    # university_name = "".join([i[0] for i in row["nombre"].split("_")])
    university_name = row["nombre"]
    university_lat = row["lat"]
    university_lon = row["lon"]

    # Calcular distancia a cada universidad
    aptosDF = aptosDF.withColumn(
        "dist_to_" + university_name,
        haversine_udf(lit(university_lat), lit(university_lon), aptosDF.lat, aptosDF.lon)
    )

distance_columns = [col for col in aptosDF.columns if col.startswith("dist_to_")]
aptosDF = aptosDF.withColumn("nearest_university", nearest_university_udf(*distance_columns))
aptosDF = aptosDF.withColumn("dist_nearest_uni", least(*distance_columns))
for col in distance_columns:
    aptosDF = aptosDF.drop(col)

# Calcular el primer cuartil y el promedio de los precios
primer_cuartil = aptosDF.approxQuantile("precio", [0.25], 0)[0]
segundo_cuartil = aptosDF.approxQuantile("precio", [0.50], 0)[0]
tercer_cuartil = aptosDF.approxQuantile("precio", [0.75], 0)[0]
promedio = aptosDF.agg(F.avg(F.col("precio"))).collect()[0][0]

# Añadir la columna de rango de precio
aptosDF = aptosDF.withColumn(
    "rango_precio",
    F.when(F.col("precio") < primer_cuartil, "economico")
    .when((F.col("precio") > primer_cuartil) & (F.col("precio") < tercer_cuartil), "medio")
    .otherwise("costoso")
)

# CREAMOS LAS VISTAS PARA PRECIO DE APTO POR UNIVERSIDAD Y NUM APTOS POR UNIVERSIDAD
promedio_precio_universidad = aptosDF.groupBy("nearest_university").agg(F.avg("precio").alias("avg_precio_apto"))
num_aptos_universidad = aptosDF.groupBy("nearest_university").agg(F.count("id_apto").alias("num_aptos"))

# AÑADIMOS LAS COLUMNAS AL DF DE UNIVERSIDADES
# Unir los dos DataFrames en uno solo
universidad_stats = promedio_precio_universidad.join(num_aptos_universidad, "nearest_university")
uniDF = uniDF.join(universidad_stats, uniDF.nombre == universidad_stats.nearest_university)
# REDONDEAR EL PRECIO
uniDF = uniDF.withColumn("avg_precio_apto", F.round(uniDF.avg_precio_apto, 1))

# UNIMOS EL DATAFRAME DE APTOS Y EL DE POSTULACIONES
joinedDF = aptosDF.join(postulacionesDF, aptosDF.id_apto == postulacionesDF.id_apto)
joinedDF = joinedDF.drop(postulacionesDF.id_apto)
# HALLAR NUMERO DE POSTULACIONES X RANGO DE PRECIO y X UNIVERSIDAD
POSTULACIONES_x_PRECIO = joinedDF.groupBy("rango_precio").agg(F.count("id_apto").alias("num_postulaciones_X_precio"))
POSTULACIONES_x_PRECIO = POSTULACIONES_x_PRECIO.withColumn("num_postulaciones_X_precio", \
                                                           F.round(POSTULACIONES_x_PRECIO.num_postulaciones_X_precio, 1))
POSTULACIONES_x_UNIVERSIDAD = joinedDF.groupBy("nearest_university").agg(F.count("id_apto").alias("num_postulaciones_X_universidad"))

# HALLAR NUMERO DE HABITACIONES POR RANGO DE PRECIO Y UNIVERSIDAD
HABITACIONES_x_PRECIO = aptosDF.groupBy("rango_precio").agg(avg("cant_h").alias("promedio_habitacion_X_rango_precio"))
HABITACIONES_x_PRECIO = HABITACIONES_x_PRECIO.withColumn("promedio_habitacion_X_rango_precio",\
                                                          F.round(HABITACIONES_x_PRECIO.promedio_habitacion_X_rango_precio, 1))
HABITACIONES_x_UNIVERSIDAD = aptosDF.groupBy("nearest_university").agg(avg("cant_h").alias("promedio_habitacion_X_universidad"))
HABITACIONES_x_UNIVERSIDAD = HABITACIONES_x_UNIVERSIDAD.withColumn("promedio_habitacion_X_universidad",\
                                                          F.round(HABITACIONES_x_UNIVERSIDAD.promedio_habitacion_X_universidad, 1))

aptos_precioDF = POSTULACIONES_x_PRECIO.join(HABITACIONES_x_PRECIO, "rango_precio")
uni_dataDF = POSTULACIONES_x_UNIVERSIDAD.join(HABITACIONES_x_UNIVERSIDAD, "nearest_university")
uni_dataDF= uni_dataDF.withColumnRenamed("nearest_university", "nombre")
uniDF = uniDF.join(uni_dataDF, "nombre")

print("Total por ocupación")
ocupacionCount.show()

print("\n"*2)
print("Universidades")
uniDF.show()

print("\n"*2)
print("Rangos de precio de aptos")
aptos_precioDF.show()

print("\n"*2)
ocupacionCount.write.csv('./db/data/ocupacionCount.csv', header=True, mode='overwrite')
uniDF.write.csv('./db/data/universidades.csv', header=True, mode='overwrite')
aptos_precioDF.write.csv('./db/data/rangosPrecio.csv', header=True, mode='overwrite')
print("Se escribieron exitosamente los archivos.")
spark.stop()