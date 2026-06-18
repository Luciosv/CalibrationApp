Proyecto: CalibrateApp

Objetivo:

CalibrateApp es una aplicación de escritorio en Python utilizando PySide6 para calibrar parámetros mecánicos de tejidos biológicos utilizados en un simulador de punción lumbar desarrollado en Unity.

La aplicación no está orientada a usuarios finales. Es una herramienta interna de calibración para el equipo de desarrollo.

Funcionamiento esperado:

* Cada tejido posee una función matemática asociada.
* Cada función posee parámetros numéricos configurables.
* El usuario puede modificar dichos parámetros mediante widgets.
* Todas las curvas de los tejidos se visualizan simultáneamente en un gráfico.
* Existe una curva de referencia cargada desde un archivo JSON.
* Los parámetros se ajustan visualmente comparando las curvas generadas con la referencia.
* Una vez calibrados, los parámetros se envían a Unity mediante WebSocket.
* Unity recibe siempre un JSON con formato ya definido.
* También debe poder exportarse el resultado a JSON y CSV.

Tecnologías obligatorias:

* Python
* PySide6
* PyQtGraph
* WebSocket

Restricciones:

* No reemplazar tecnologías.
* No modificar la organización general de la interfaz.
* No rediseñar la UI.
* No eliminar funcionalidades existentes.
* No introducir frameworks innecesarios.

Distribución visual obligatoria:

* Gráfico principal grande en la zona izquierda.
* Panel de parámetros a la derecha.
* Barra superior con botones para:

  * Cargar JSON de referencia.
  * Restaurar parámetros base.
  * Enviar a Unity.
  * Exportar JSON.
  * Exportar CSV.

Arquitectura actual:

project/
├── main.py
├── config/
├── models/
├── math/
├── network/
├── ui/
└── utils/

Problemas conocidos:

1. El sistema de parámetros no está centralizado.
2. Los datos de parámetros no se almacenan de forma consistente.
3. Los widgets de edición de parámetros están incompletos.
4. Existen responsabilidades mezcladas entre UI y datos.
5. La conexión final con Unity aún debe completarse.

Prioridades:

1. Correctitud funcional.
2. Mantenibilidad.
3. Claridad del código.
4. Extensibilidad para agregar nuevas funciones matemáticas.
5. Robustez del flujo JSON.

Utiliza esta información como contexto permanente para todas las tareas posteriores.
