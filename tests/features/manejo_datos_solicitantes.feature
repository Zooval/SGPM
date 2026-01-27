# Created by anthony at 10/1/2026
# language: es

@solicitantes @datos
Característica: Manejo de datos de los solicitantes
  Como asesor
  Quiero gestionar la información de los solicitantes de un proceso migratorio
  Para mantener sus datos actualizados y dar seguimiento a su proceso

  Antecedentes:
  Dado que soy un asesor autenticado

  Regla: La cédula identifica de forma única al solicitante
  Regla: Los campos obligatorios deben estar completos para registrar o actualizar

    @critico @feliz
    Escenario: Registrar un solicitante con datos obligatorios completos
      Dado que no existe un solicitante con cédula "0102030405"
      Cuando registro un solicitante con los siguientes datos:
        | cedula     | nombre | apellido | correo              | fecha_nacimiento | telefono   | direccion        |
        | 0102030405 | Ana    | Torres   | ana.torres@mail.com | 1998-05-12       | 0998765432| Av. Amazonas 123 |
      Entonces el solicitante queda registrado correctamente
      Y puedo visualizar la ficha del solicitante con cédula "0102030405"

    @feliz
    Escenario: Actualizar datos de contacto de un solicitante existente
      Dado que existe un solicitante con los siguientes datos:
        | cedula     | nombre | apellido | correo              | fecha_nacimiento | telefono   | direccion        |
        | 0102030405 | Ana    | Torres   | ana.torres@mail.com | 1998-05-12       | 0998765432| Av. Amazonas 123 |
      Cuando actualizo los datos de contacto del solicitante con cédula "0102030405":
        | correo                    | telefono   | direccion        |
        | ana.torres.nuevo@mail.com | 0987654321 | Calle Colón 456  |
      Entonces los cambios se guardan correctamente
      Y la ficha del solicitante muestra los datos actualizados

    @validacion
    Esquema del escenario: Evitar registrar un solicitante si falta un dato obligatorio
      Dado que no existe un solicitante con cédula "<cedula>"
      Cuando intento registrar un solicitante con los siguientes datos:
        | cedula   | nombre   | apellido   | correo   | fecha_nacimiento | telefono   | direccion   |
        | <cedula> | <nombre> | <apellido> | <correo> | <fecha>          | <telefono> | <direccion> |
      Entonces se muestra un mensaje de error por datos obligatorios
      Y el solicitante con cédula "<cedula>" no se registra

      Ejemplos:
        | cedula     | nombre | apellido | correo              | fecha      | telefono   | direccion       |
        | 0102030406 |        | Pérez    | sin.nombre@mail.com | 2000-01-10 | 0912345678 | Av. Central 789 |

    @regla_negocio
    Escenario: Evitar registrar un solicitante con cédula ya registrada
      Dado que existe un solicitante con los siguientes datos:
        | cedula     | nombre | apellido | correo              | fecha_nacimiento | telefono   | direccion        |
        | 0102030405 | Ana    | Torres   | ana.torres@mail.com | 1998-05-12       | 0998765432| Av. Amazonas 123 |
      Cuando intento registrar un solicitante con los siguientes datos:
        | cedula     | nombre | apellido | correo               | fecha_nacimiento | telefono   | direccion        |
        | 0102030405 | Carlos | Vera     | carlos.vera@mail.com | 1995-08-20       | 0976543210| Calle Loja 321   |
      Entonces se muestra un mensaje indicando que la cédula ya está registrada
      Y no se crea un nuevo solicitante