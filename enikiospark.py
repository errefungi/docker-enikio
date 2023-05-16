import requests
from pyspark.sql.functions import udf, col, lit, least, when, avg
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
    university_names = [" ".join(name.split("_")[2:]) for name in distance_columns]
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
aptosDF = aptosDF.select("id_apto", "precio", "cant_h", "lat", "lon")
uniDF = uniDF.select("nombre", "lat", "lon")
# result = postulacionesDF.groupBy("ocupacion").count()

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

# Añadir la columna de rango de precio
primer_cuartil = aptosDF.approxQuantile("precio", [0.25], 0)[0]
promedio = aptosDF.agg(avg(col("precio"))).collect()[0][0]


aptosDF = aptosDF.withColumn(
    "rango_precio",
    when(col("precio") < primer_cuartil, "economico")
    .when((col("precio") >= promedio - 10000) & (col("precio") <= promedio + 10000), "medio")
    .otherwise("costoso")
)

# print("Total por ocupación")
# result.show(10)
# print("\n"*2)
print("Aptos")
aptosDF.show(5)
# print("\n"*2)
# print("Universidades")
# uniDF.show()
# spark.stop()