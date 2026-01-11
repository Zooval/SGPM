# Created by ximen at 10/1/2026
# language: es

Característica: Manejo de datos de los migrantes
  Se encarga del registro de la información de los clientes que solicitan un proceso migratorio,
  la actualización de la información de los mismos, en sí la gestión de los migrantes.

  HU-01: Registrar migrante
  Como asesor
  Quiero registrar la información personal y migratoria del migrante
  Para iniciar su trámite migratorio según su condición y destino

  Esquema del escenario: Registro exitoso de migrante
    Dado que un cliente ha solicitado iniciar un trámite migratorio
    Cuando el asesor registra la información del migrante con los siguientes datos:
      | cedula   | nombre   | edad   | estado_civil | ocupacion   | condicion   | tipo_visa | pais_destino | telefono   | correo   | direccion   | foto   |
      | <cedula> | <nombre> | <edad> | <estado>     | <ocupacion> | <condicion> | <visa>    | <pais>       | <telefono> | <correo> | <direccion> | <foto> |
    Entonces el migrante queda caracterizado según su condición migratoria
    Y el trámite de visa queda definido según el tipo y país de destino
    Y el migrante cuenta con una imagen de identificación registrada

    Ejemplos:
      | cedula     | nombre       | edad | estado  | ocupacion | visa     | condicion  | pais     | telefono   | correo                | direccion | foto              |
      | 0605914283 | Daniel Pérez | 27   | Soltero | Trabajo   | Trabajar | Inmigrante | Canadá   | 0991234567 | daniel.perez@mail.com | Quito     | daniel_perez.jpg  |
      | 1712098475 | María Gómez  | 22   | Soltera | Estudio   | Estudiar | Emigrante  | España   | 0987654321 | maria.gomez@mail.com  | Guayaquil | maria_gomez.png   |
      | 0912385423 | Luis Andrade | 35   | Casado  | Trabajo   | Vivir    | Emigrante  | Alemania | 0971122334 | l.andrade@mail.com    | Cuenca    | luis_andrade.jpeg |

  #Escenarios alternativo
  Esquema del escenario: Migrante previamente registrado
    Dado que existe un migrante registrado con la cédula "<cedula>"
    Cuando el asesor intenta registrar nuevamente al migrante
    Entonces se reutiliza la información existente
    Y se asocia al nuevo trámite

    Ejemplos:
      | cedula     |
      | 0605914283 |

  Esquema del escenario: Registro sin fotografía
    Dado que un cliente solicita iniciar un trámite migratorio
    Cuando el asesor registra la información del migrante sin fotografía
    Entonces el migrante queda registrado
    Y la fotografía queda pendiente de carga

    Ejemplos:
      | cedula     | nombre      |
      | 1712098475 | María Gómez |


