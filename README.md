# Buenaventura agronegocios

## Configuración de Docker

Los entornos de desarrollo, staging y producción están configurados en OTRO repositorio [infra](https://github.com/wilitp/infra-buenaventura). En este repositorio tenemos solo el código fuente de la aplicación y symlinks a los archivos de configuración que deberían estar bajo el directorio `infra` debajo del root de este repositorio.

Si no está el repositorio `infra`, clonarlo en esa ubicación.

Es importante que se incluya `infra` en el `.gitignore` así uno puede cambiar de versión de la configuración de manera independendiente con la versión de la aplicación.

## Como iniciar el proyecto en local

Una vez clonado este repo y luego clonado en `infra` el repo con la configuración de docker, correr:

```bash
docker compose up -d 
```


## Migraciones

Para ejecutar comandos de django dentro del contenedor:

```bash
docker compose exec app ash
```

Las migraciones son código legible para humanos y parte del proyecto. No siempre se generan automáticamente y deberías entenderlas antes de pushearlas.

Cada vez que se hace un cambio a los modelos y se necesiten migraciones sobre la base de datos:

- Generar(con `python manage.py makemigrations`) / escribir las migraciones necesarias para los cambios en los modelos
- Correr las migraciones en el contenedor local (`python manage.py migrate`)
- Probar que se puedan hacer todas las operaciones referidas al modelo modificado
- COMMITEAR LOS CAMBIOS AL MODELO Y LAS MIGRACIONES EN UN SOLO COMMIT

Si se siguen estos pasos, será muy improbable tener errores de migraciones en producción y será fácil usar cambios de otros sin necesidad de entender que hicieron para hacer que nuestra base local se amolde a sus cambios.




