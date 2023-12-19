# decide-part-pantoja-1
* grupo 2
* Curso escolar: 2023/2024
* Asignatura: Evolución y gestión de la configuración
## Miembros del equipo 

| Miembro | Implicación |
| ------------- | ------------- |
| [Baquero Fernández, Fernando](https://github.com/ferbaqfer) | [10]
| [Carbó Sánchez, Jaime Ramón](https://github.com/jaime-carbo) | [10] |
| [Cortés Fonseca, Daniel](https://github.com/nombredeusuariodegithub) | [10] |
| [Jiménez Medina, Eloy](https://github.com/nombredeusuariodegithub) | [10] |
| [Peláez Moreno, Antonio](https://github.com/antoniopelaezmoreno) | [10] |

## Enlaces de interés:
* [Repositorio de código](https://github.com/part-pantoja/decide/) 
* [Sistema desplegado en pythonanywhere](https://decidepantoja.pythonanywhere.com/) 
* [Sistema desplegado en render](https://decidepantoja.onrender.com/) 




### Indicadores del proyecto

* [Enlace a captura de git fame](https://github.com/part-pantoja/decide/blob/main/doc/Commits%20main%20Git%20Fame(No%20recoge%20todos).jpeg)

Miembro del equipo  | Horas | Commits | LoC | Test | Issues | Incremento |
------------- | ------------- | ------------- | ------------- | ------------- | ------------- |  ------------- | 
[Baquero Fernández, Fernando](https://github.com/ferbaqfer) | 64 | 26 | 766 | 7 | 7 | Creación de votaciones, administración de votaciones y estadísticas de algunos tipos de votaciones, todo desde la página principal (no desde el panel)
[Carbó Sánchez, Jaime Ramón](https://github.com/jaime-carbo) | 62 | 40 | 729 | 6 | 15 | Plantillas issues, github actions conventional commits, opción votos en blanco, despliegue en docker e intento en vagrant
[Cortés Fonseca, Daniel](https://github.com/nombredeusuariodegithub) | 66 | 27 | 1052 | 9 | 7 | Registro de página con verificación por código enviado al correo y login mediante username y correo.
[Jiménez Medina, Eloy](https://github.com/nombredeusuariodegithub) |68 |  36 | 446 | 6 | 9 | Implementación home y módulo request, que consiste en solicitud de ser añadido al censo. Todo desde la interfaz.
[Peláez Moreno, Antonio](https://github.com/antoniopelaezmoreno) | 62 | 22 | 440 | 7 | 7 | Diseño de un nuevo tipo de votación: Votación de respuesta abierta, su cabina para la votación y el postprocesado. También una interfaz para añadir votantes al censo de una votación.
**TOTAL** | 322  | 137 | 3433 | 35 | 44 | Lo indicado anteriormente 


### Integración con otros equipos
Equipos con los que se ha integrado y los motivos por lo que lo ha hecho y lugar en el que se ha dado la integración: 
* [part-pantoja-2](https://github.com/part-pantoja/decide/): Ambos equipos hemos realizado diferentes incrementos funcionales de múltiples módulos en el mismo repositorio.

## Resumen ejecutivo
El trabajo que hemos realizado tiene como nombre: ‘decide-part-pantoja-1”. Este proyecto ha alcanzado importantes logros en la implementación de una aplicación de voto electrónico. Se ha realizado con python 3.10 y, en concreto, con el framework de django. Debemos destacar que, al ser un proyecto de tipo part, se ha colaborado con el grupo ‘part-pantoja-2’, lo que ha supuesto un trabajo adicional para ambos equipos.

Durante la fase inicial, la orientación del tutor resultó crucial. Las recomendaciones recibidas durante la revisión en el M1 se centraron en la cohesión entre los incrementos planificados. Este feedback influyó en la planificación del equipo, refinando el enfoque para lograr una implementación más coherente y eficaz de las mejoras propuestas, ya que los incrementos funcionales que teníamos pensados no tenían relación entre sí.

Con respecto a los incrementos funcionales, encontramos la implementación de un nuevo tipo de votación llamado "Respuesta Abierta", permitiendo a los usuarios expresar sus preferencias mediante respuestas numéricas escritas.

Además, se ha puesto énfasis en mejorar la interfaz de usuario para hacerla más accesible y fácil de usar. Estas mejoras abarcan la simplificación del proceso de creación de votaciones y la inclusión de personas en el censo electoral, añadiendo las comprobaciones de existencia de usuarios y/o votaciones en el sistema.

Por otro lado, se ha implementado un sistema de registro e inicio de sesión personalizado que incluye campos como la  dirección de correo electrónico. Cada campo del formulario de registro se ha diseñado con restricciones de seguridad, asegurando la integridad y confidencialidad de la información del usuario.

Reconociendo la importancia de representar todas las preferencias del votante, se ha incorporado la opción de voto en blanco, de forma que si el creador de la votación quiere, se podrá añadir esta opción entre las demás.

Por último,  se ha implementado la funcionalidad de vistas de resultados para las votaciones en el proyecto. Una vez finalizadas las votaciones y realizado el recuento, se presenta una pantalla de estadísticas y resultados específica para cada tipo de votación. Estas pantallas varían según el tipo de votación, ofreciendo una representación visual y comprensible de los resultados obtenidos.

Las pruebas exhaustivas desempeñaron un papel central en el proyecto. Se llevaron a cabo pruebas unitarias para evaluar la funcionalidad individual de cada componente. También se han realizado pruebas de interfaz, mediante el uso de la extensión de ‘Selenium’, además de pruebas de carga con ‘Locust’.

En el desarrollo del proyecto, se adoptó la metodología Gitflow como enfoque principal para gestionar el flujo de trabajo. Esta elección se basó en la conveniencia que brinda Gitflow al permitir un manejo más eficiente de las funcionalidades, especialmente cuando se trabaja en un proyecto con múltiples integrantes y módulos.

Gitflow facilitó la colaboración al utilizar ramas (o troncos) intermedias que agrupaban los cambios por módulos específicos. Este enfoque modular no solo simplificó la colaboración entre miembros del equipo, sino que también permitió un desarrollo más organizado y estructurado, ayudando en la integración del trabajo de los desarrolladores.

### Descripción del sistema

El sistema desarrollado es una plataforma de voto electrónico educativa denominada "Decide". Su principal objetivo es proporcionar un entorno seguro y eficiente para la realización de votaciones, en la que los participantes mantengan total anonimato.

*DESCRIPCIÓN FUNCIONAL*
#### 1. **Sistema de Votación Electrónica Segura:**
   - **Anonimato y Secreto del Voto:** La plataforma garantiza la anonimicidad de los votantes y el secreto del voto, asegurando que cada participante pueda expresar su elección de manera confidencial.

#### 2. **División en Subsistemas:**
   - **Desacoplamiento Modular:** La arquitectura del sistema se divide en subsistemas , lo que facilita la sustitución y extensión de módulos sin afectar a la integridad del sistema.

#### 3. **Configuración y Ejecución del Proyecto:**
   - **Personalización con local_settings.py:** Permite la configuración personalizada mediante un archivo `local_settings.py`, donde se definen rutas y módulos específicos del proyecto.
   - **Gestión de Dependencias:** Utiliza Pip y un archivo `requirements.txt` para gestionar las dependencias del proyecto.

#### 4. **Pruebas Automatizadas y Cobertura de Código:**
   - **Suite de Pruebas Unitarias:** Incorpora una amplio repertorio de pruebas para verificar el correcto funcionamiento de las diversas funcionalidades del sistema.
   - **Cobertura de Código:** Utiliza Codacy para identificar áreas del código que no han sido testeadas y mejorar la calidad de la sintaxis del código.

#### 5. **Interfaz de Administración y Gestión de Usuarios:**
   - **Panel Administrativo Intuitivo:** Proporciona un panel de administración intuitivo para la gestión de preguntas, votaciones y usuarios.
   - **Roles de Usuario:** Define roles como administradores y votantes, con permisos específicos para garantizar la seguridad y el control de acceso.

#### 6. **Carga Inicial de Datos y Población:**
   - **Archivo JSON para Datos Iniciales:** Facilita la prueba del sistema mediante un archivo JSON (`populate.json`) que carga datos iniciales, incluyendo usuarios y votaciones.

#### 7. **Tests de Estrés con Locust:**
   - **Pruebas de Estrés Automatizadas:** Utiliza Locust para realizar pruebas de estrés automatizadas y evaluar el rendimiento del sistema bajo diferentes cargas simuladas.

#### 8. **Visualización de Resultados y Conteo:**
   - **Interfaz para Resultados:** Ofrece una interfaz para la visualización de resultados de votaciones y el conteo de votos.
   - **Guía para el Proceso de Votación:** Facilita el proceso de votación guiando a los usuarios a través de las diferentes etapas de manera clara y efectiva.

#### 9. **Despliegue con Docker y PythonAnywhere:**
   - **Contenedores Docker:** Configura contenedores Docker para simplificar el despliegue y la gestión de dependencias. Concretamente son 3 los contenedores que son lanzados simultáneamente con docker compose.
   - **Despliegue con PythonAnywhere:** version desplegada permanentemente en la web con pythonanywhere.


#### 10. **Versiones Actuales de Tecnologías Utilizadas:**
   - **Django 4.1, Vue 3, Bootstrap 5.2, y Más:** Emplea las versiones más recientes de tecnologías clave para garantizar la compatibilidad y aprovechar las últimas características y mejoras.

*INCREMENTOS FUNCIONALES*

#### 1 Adiciones a la interfaz de la página principal
* **Creación de una votación desde la página principal sin necesidad de entrar en el panel de administrador.**
#### 2 Despliegue
* **Desplegado en docker y vagrant**
* **Desplegado en la web en pythonanywhere y en render** 
#### 3 Nuevos tipos de votaciones
* **Apartado de administrar votación y detalles de votación para el admin.**
* **Añadir opción de voto en blanco al crear una pregunta.**
* **Apartado de administrar votación y detalles de votación para el admin.**
#### 4 Estadísticas de votaciones
* **Creación de estadísticas en el visualizer para las votaciones de tipo single choice y open response.**
#### 5 Mejoras del repositorio
* **4 plantillas para especificar issues de nueva feature, tests, bugfixes  y documentación.**
* **Workflow para verificar si se esta siguiendo la nomenclatura de commits "conventional commits".**
#### 6 Otros
* **Creación de un registro personalizado y modificación del login por otro personalizado. En el registro te piden datos como nombre de usuario, correo electronico y la contraseña. Todos los campos del registro estan adecuados con las correspondientes restricciones de seguridad. Al registrarte en la pagina, se te envia un codigo de verificacion al correo indicado durante el registro, el cual tendrás que copiar y pegar en la página redireccionada para que se te active la cuenta. Una vez registrado podras hacer uso de las funcionalidades de la página y podras volver a iniciar sesión con tu nombre de usuario o tu correo electrónico.**
* **Modulo home, implementación de una pantalla de home, juntos a una navbar para unificar el diseño de la web.**
* **Modulo request, permite a un usuario solicitar ser añadido a una votación. Dicha solicitud debe ser aceptada o denegada por el administrador. Tras la decisión, recibirás un email con la decisión. Todo desde la interfaz.**








### Visión global del proceso de desarrollo
El proceso de desarrollo en nuestro proyecto de votaciones en línea implica varias etapas clave que están intrínsecamente ligadas al ciclo de vida del desarrollo del software. A lo largo de este proceso, hemos empleado diversas herramientas que han facilitado y optimizado cada fase del desarrollo. A continuación, se presenta una descripción detallada de cada etapa seguida en el desarrollo del proyecto:

#### 1. Diseño de Nuevas Funcionalidades:
En esta fase, nos hemos enfocado en identificar y diseñar las nuevas funcionalidades que mejorarán nuestro sistema de votación. Partiendo de esta premisa, decidimos que cada integrante propusiera una mejora funcional al sistema. Tras una reunión inicial se decidieron y definieron de manera muy básica los distintos implementos que realizaría cada integrante y fueron los siguientes:
- Creación de votaciones las cuales tengan asociada un pregunta de tipo Multiple Respuesta, en la que al realizar la votación pudieras marcar varias respuestas.
- Creación de votaciones las cuales tengan asociada un pregunta de tipo SiNo, en la que al realizar la votación las únicas posibles respuestas fueran Si o No.
- Creación de votaciones las cuales tengan asociada un pregunta de tipo Orden, en la que al realizar la votación pudieras ordenar las respuestas de la misma según tu criterio.
- Creación de votaciones las cuales tengan asociada un pregunta de tipo Puntos, en la que al realizar la votación pudieras asignar a cada respuesta un peso o unos puntos, repartiendo los que te permite la propia votación(si te da 10 puntos, pues tienes que repartirlos entre las distintas respuestas).
- Creación de votaciones las cuales tengan asociada varias preguntas de tipo Simple, en la que al realizar la votación puedas responder todas ellas.
- Creación de una interfaz para el usuario en la que pueda acceder a las distintas votaciones y si tiene el rol pertinente, poder crearlas, modificarlas, empezarlas...


#### 2. Desarrollo de Funcionalidades:
Con el diseño en su lugar, nos sumergimos en la fase de desarrollo. Hemos utilizado herramientas de desarrollo colaborativas, usando Git como controlador de versiones y gestor de repositorios y GitHub como servicio de alojamiento en remoto para el trabajo conjunto entre los integrantes de nuestro equipo y los de la otra parte. Esto ha facilitado una programación eficiente en la que cada miembro tenia acceso al código actualizado de manera permanente. Así mismo para la organización de las ramas en el repositorio hemos seguido el modelo de GitFlow, organizando las ramas según su propósito, features si son para realizar funcionalidad, hotfix si son para realizar correcciones importantes en el código debido a algún bug, una rama main/master que se convertirá en la release(de ella saldrá) y una rama develop en la que ira actualizando el código en desarrollo de manera continua, CI.

#### 3. Pruebas y Validación:
Una vez finalizada la implementación, dedicamos tiempo a llevar a cabo pruebas en las distintas funcionalidades creadas con un enfoque integral respaldado por herramientas como GitHub Actions. Hemos implementado un proceso de integración continua mediante GitHub Actions, automatizando pruebas para garantizar la estabilidad y la funcionalidad esperada del proyecto. Esto nos permitía asegurar que todo el código presente en la rama de desarrollo funcionaba de manera correcta, lo que nos aportaba seguridad en la combinación de las distintas funcionalidades.

Además de las pruebas automatizadas, hemos realizado pruebas manuales para evaluar la experiencia del usuario desde un punto de vista más gráfico, asegurándonos de que las nuevas funcionalidades se integren de manera coherente con las existentes. Este enfoque híbrido, combinando pruebas automatizadas y manuales, nos ha permitido obtener una visión completa de la calidad del software.

Para fortalecer nuestro proceso, hemos desplegado el proyecto en un servidor remoto utilizando PythonAnywhere mediante GitHub Actions, lo que nos permitía tener una aplicación funcionando y actualizada accesible por todos los miembros del equipo. Por último, configuración de nuestro repositorio en Codacy lo que nos permitía realizar un análisis de código estático de manera continua, identificando posibles problemas y proporcionando recomendaciones para mejorar la calidad del código, así como generándonos un informe de cobertura del proyecto.

Este proceso de integración continua nos permitía encontrar errores en el código de manera mas tempranas elaborando pruebas para cada funcionalidad y ejecutando las mismas de manera automática.

#### 4. Preproducción:
La fase de preproducción ha sido esencial para identificar posibles problemas antes de lanzar la versión final del sistema. Hemos utilizado entornos de prueba que replican el entorno de producción y hemos realizado pruebas adicionales de carga y rendimiento para garantizar la eficiencia del sistema en situaciones de uso intensivo.

#### 5. Producción:
Finalmente, hemos llevado nuestro proyecto a producción. Hemos utilizado herramientas de implementación continua para garantizar una implementación sin problemas. La monitorización constante del sistema nos permite identificar y abordar cualquier problema que pueda surgir en tiempo real, garantizando la disponibilidad y la confiabilidad del sistema para los usuarios finales. Así como la organización del proyecto en contenedores usando los servicios que nos proporciona Docker

#### Ejemplo de Cambio Propuesto:
Imaginemos que se propone agregar una nueva opción de votación que permita a los usuarios asignar una nota a cada opción(del 1 al 10 por ejemplo). Esto implica cambios en la interfaz de usuario, lógica de votación y almacenamiento de datos así como postprocesado de los mismos. El proceso para abordar este cambio sería el siguiente:

##### Diseño:
- Identificar requisitos específicos para la nueva funcionalidad.
- Crear diseños de interfaz de usuario que reflejen la opción de asignar notas a las respuestas.
- Crear una incidencia de tipo New Feature en la que se recoja de manera detallada tanto la lógica esperada como el diseño de la nueva funcionalidad realizado.

##### Desarrollo:
- Creación de una rama feature para esta funcionalidad, la cual seguirá el formato feature/nuevaVotación.
- Implementar la lógica de votación con notas.
- Actualizar la base de datos para almacenar la información de los votos asociados a cada respuesta.

##### Pruebas y Validación:
- Una vez creada la funcionalidad se realizarán las pruebas pertinentes guiándonos por las funciones CRUD, errores conocidos y en caso de que sea necesario, valores limite.
- Estas pruebas se automatizarán para garantizar la integridad de la nueva funcionalidad.
- Llevaremos a cabo pruebas manuales para evaluar la usabilidad y la experiencia del usuario a lo largo de todo el proceso.
- Una vez realizadas las pruebas, se cerrará la issue, o bien de manera manual o bien asociándola a la pull request la cual estará marcada por la aprobación tanto de GitHub Actions como de un integrante que la revisará.


#### Preproducción:

- Una vez pasadas las pruebas y desplegado el proyecto, se analizará la cobertura reflejada en Codacy generando un informe de la misma. 
- Posteriormente probaremos la funcionalidad de la votación en un entorno controlado que simule el entorno de producción.

#### Producción:

- Implementar la funcionalidad de la votación en el entorno de producción.
- Monitorear el sistema para detectar cualquier problema y realizar ajustes según sea necesario.

Este enfoque holístico en el desarrollo, desde el diseño hasta la implementación y más allá, nos ha permitido ofrecer un sistema de votación robusto y adaptable a medida que evolucionan los requisitos y las necesidades de los usuarios.

### Entorno de desarrollo
El entorno de desarrollo utilizado para la creación de la aplicación Django se basa en Visual Studio Code con Python 3.10. A continuación, se proporciona una explicación detallada sobre el entorno, las versiones utilizadas y los pasos necesarios para instalar el sistema y los subsistemas relacionados.

#### **Entorno de desarrollo**
##### **1. Visual Studio Code:**
Visual Studio Code (VS Code) es el entorno de desarrollo integrado (IDE) seleccionado para la creación de la aplicación Django. Es un IDE ligero y potente que ofrece una amplia gama de extensiones para diferentes lenguajes de programación, incluido Python.

##### **2. Python 3.10:**
La versión 3.10 de Python es la utilizada para el desarrollo de la aplicación. Python es el lenguaje de programación principal en el que se basa Django, y la versión 3.10 incluye nuevas características y mejoras.

#### **Librerías y dependencias**
Se han utilizado varias librerías y dependencias para el desarrollo de la aplicación, y se han especificado en el archivo requirements.txt. Aquí están las principales librerías junto con sus versiones correspondientes:
* Django (4.1): El framework web de alto nivel en Python que facilita el desarrollo rápido y limpio.

* pycryptodome (3.15.0): Una biblioteca de criptografía que proporciona implementaciones seguras de varios algoritmos criptográficos.

* djangorestframework (3.14.0): Una potente y flexible herramienta para construir APIs web.

* django-cors-headers (3.13.0): Una aplicación Django para manejar encabezados CORS (Cross-Origin Resource Sharing).

* requests (2.28.1): Una biblioteca HTTP para Python que facilita el envío de solicitudes HTTP.

* django-filter (22.1): Una aplicación de filtrado para Django.

* psycopg2 (2.9.4): Adaptador de base de datos PostgreSQL para Python.

* coverage (6.5.0): Una herramienta para medir la cobertura de código de Python.

* jsonnet (0.18.0): Un lenguaje de configuración de datos que permite la creación de archivos de configuración JSON de manera más concisa.

* django-nose (1.4.6): Integración de Nose para Django, una extensión de prueba.

* django-rest-swagger (2.2.0): Una interfaz gráfica para la documentación de API en Django REST Framework.

* selenium (4.7.2): Una herramienta para la automatización de navegadores web.

* pynose (1.4.8): Extiende pruebas unitarias y hace el testeo más fácil.

* locust (2.20.0): Herramienta para las pruebas de carga y evaluar el rendimiento de nuestra aplicación.


#### **Pasos para la Instalación:**
##### 1. Configurar Entorno Virtual:
Crea un entorno virtual para aislar las dependencias del proyecto.
* python3.10 -m venv venv
source venv/bin/activate  # Para sistemas basados en Unix

##### 2. Configurar claves SSH con GitHub
* Generar claves: ssh-keygen -t rsa -b 4096
* Visualizar clave pública y copiar: cat id_rsa.pub
* Añadir la clave a GitHub

##### 3. Clonar el repositorio
Clona el repositorio de la aplicación Django desde GitHub:
* git clone https://github.com/part-pantoja/decide

##### 4. Instalar Dependencias:
Utiliza pip para instalar las dependencias del archivo requirements.txt.
* pip install -r requirements.txt

##### 5. Crear base de datos:
* sudo su - postgres
* psql -c "create user decideuser with password 'decidepass123'"
* psql -c "create database decidedb owner decideuser"

##### 6. Modificación de local_settings.py:
En el archivo local_settings.py nos aseguraremos que en el apartado DATABASES, los atributos 'NAME','USER' y 'PASSWORD', tienen los valores de la base de datos creada previamente. También nos aseguraremos de que el atributo 'HOST' tiene el valor 'localhost'.

##### 7. Aplicar Migraciones:
Aplica las migraciones de la base de datos para inicializarla.
* python manage.py makemigrations
* python manage.py migrate

##### 8. Crear Superusuario (Opcional):
Si es necesario, crea un superusuario para acceder al panel de administración de Django.
* python manage.py createsuperuser

##### 9. Ejecutar Servidor de Desarrollo:
Inicia el servidor de desarrollo de Django.
* python manage.py runserver

La aplicación estará disponible en http://localhost:8000/.

Estos pasos aseguran la instalación adecuada de las dependencias y la configuración del entorno de desarrollo. Es importante tener en cuenta que estos pasos asumen un entorno Unix; si se utiliza un entorno diferente, los comandos pueden variar ligeramente.


### Ejercicio de propuesta de cambio
# Propuesta de cambio: Modo claro/oscuro en interfaz

  

En primer lugar, deberemos crear una rama desde la versión más actualizada de nuestro proyecto.

  

Para ello, podemos hacer clic, desde nuestro repositorio GitHub, en **New Branch**, seleccionando dicha rama. La llamaremos `feature/LightDarkMode`.

  

Ahora crearemos la issue de la funcionalidad que queremos implementar. Para ello, haremos click en el menú Issue y seguidamente le daremos a New Issue.

  

Le pondremos nombre: **Nueva funcionalidad: LightDarkMode**. Asumo que su ID es 1.

  

Una vez hayamos creado la rama y la issue, iremos a nuestro IDE, en mi caso VSC, y escribiremos en consola:

  

```bash
git  fetch
```

Este comando nos proporciona todas las ramas del repositorio en la nube.

Ahora queremos saltar a la nueva rama. Usaremos el comando:
```bash
git checkout feature/LightDarkMode_
```
Comprobaremos con _git checkout_ nuevamente si hemos cambiado correctamente de rama.

Una vez en la rama, realizamos todos los cambios necesarios para cumplir con la funcionalidad.

El trabajo puede consistir en lo siguiente:

Crear dos base.html, de los cuales extenderán el resto de plantillas. Uno será light y otro dark. Dependiendo del valor de una variable, que se puede cambiar con un botón, se aplicará un base.html u otro.

Una vez realizados todos los cambios necesarios, usamos el siguiente comando para añadir las modificaciones al commit:
```bash
git  add .
```

Ahora procedemos a hacer el commit:
```bash
git commit -m “feat: LightDarkMode #1 
```

Por último, usamos git push origin master para actualizar el repositorio con este commit.

Por último, deberemos crear una pull request a la rama que interese, en mi caso develop, y asignar a algún compañero la revisión de esta.

Una vez aceptada, ya habremos implementado la funcionalidad.


# Conclusiones
En conclusión, el proyecto decide-part-pantoja-1 ha logrado avances significativos en el ámbito de las aplicaciones de voto electrónico. Con una base tecnológica sólida, interfaz mejorada y nuevas características de votación, el proyecto se presenta como una solución moderna y adaptable para futuras necesidades en el ámbito de la participación electoral digital.
# Trabajo futuro
## Listado de posibles tareas a desarrollar:

### Autenticación
- Autenticación por certificado digital
- Autenticación con Google
- Autenticación con OAuth

### Censo
- Importación y exportación de censo.
- Retirar censo desde frontend.
- Grupos de censo

### Votación
- Interfaz para crear nuevos tipos de votación.
- Interfaz para crear una Question.
