# Pruebas generales de firmware y hardware

El objetivo de las pruebas es validar el hardware y firmware tal que cumpla con las funciones requeridas. Especificamente:

1. Validar el funcionamiento del hardware especifico en sus variaciones AC, DC y LoRa.

2. Observar el desempeño del hardware en el recinto, disposición fisica de los conductores y agujeros.

3. Verificar el rendimiento del hardware bajo condiciones físicas y electricas de estrés (temperatura, polvo, ruidio eléctrico y vibración).

4. Validar los modulos de comunicación tanto serial interna, serial externa e inalambrica.

5. Verificar el rendimiento del hardware bajo condiciones de estrés de información (baurate, tiempo entre tramas, tramas no validas).

6. Verificar la exactitud de la medición medición de energía.


7. Observar defectos de rendimiento y bugs.


# 1. Validar funcionalidad general del hardware

Se debe verificar que el hardware diseñado energice propiadamente el MCU, y este se comunique correctamente con los perifericos como lo son los terminales para EN y BOOT, el transceptor RS485 y el transceptos LoRa. Esto se logra de la siguiente manera.

## 1.1 MCU operativo

Lo primero que se debe verificar es que el MCU este activo, para esto se monitorea los terminales asociados al UART0 en la computadora, donde se debe mostrar un mensaje de las caracteriticas del MCU en color verde, esto es un programa por defecto, no se necesita quemar nada para ver esto. Este mensaje debe repetirse cada vez que se cortocircuitan los terminales de EN.

Luego se corrobora que el MCU pueda entrar y salir del boot a partir de la combinación de cortocituitos entre BOOT y EN.

Para entrar a *boot*,  presione EN con BOOT presionado durante y previamente. Debera presenciar un mensaje de `Waiting for flash...`, indicando que esta listo para ser quemado con el programada deseado.

Para salir de *boot* solo reinicie cortocircuitando EN. El MCU debera iniciar el programa inmediatamente, proporcinando logs coherentes en el UART0.

Cada reinicio debe presentar 3 pulsos consecutivos en el LED de diagnostico

## 1.2 Contador de pulsos

Al cortocircuitar los pines de VDD y P-in se debe presentar un log de que un pulso a sido registrado. Asi como un pulso en el LED diagnostico.

## 1.3 Transceptor RS485

Con el MCU configurado como Maestro modbus, se puede verificar que este reciba y envia correctamente tramas de información a través del tranceptor RS485. Con ayuda de un adaptador RS485 a usb, se monitorea en la computadora dicho puerto configurado a 9600 baudios, 1 bit de parada con paridad impar.

Se deberan observar tramas validas modbus de interrogación a esclavos con la funcion 4 modbus, de manera constante (1,2,3,1,2,3,...). De la misma manera si se envian datos hexadecimales estos de deben reflejar en los logs del MCU, si es una trama valida modbus esto tambien se debe reflejar.


## 1.4 Tranceptor LoRa

Los chip LoRa son configurados bajo el mismo ID del nodo en si, asi que debe consultar dicho ID usando otro disposivo LoRa, los logs de MCU deberan presentar las tramas coherentes con las información solitada. Además de un parpadeo intermitente de los LED integrados en chip LoRa (azul cuando se recibe y rojo cuando se envía).


### Resultados y observaciones

## 2. Recinto y dispoción física
 
La  PCB debe entrar comodamente el caja para la cual fue diseñada, considerando los conductores que se deben conectar a ella, así como la antena cuando aplique.

Los tornillos deberan coincidir con los agujeros destinados para ellos, así tambien el diametro de los mismos.

El agujero de la antena debe ser posicionado a un lateral de tal manera que sea facil extraer y colocar la PCB.


## 3. Estres físico

Se debe  el comportamiento normal y recuperación del hardware en condicion abnormales del ambiente. Sometiendolo a cambios de temperatura (15-40), exposición al sol, cambios de humedad (rocio), vibración (a través de un taladro), perturbación electricas (apagado rependino, rudio electrico de taladro).


El sistema de continuar funcionando normalmente en estar circustancias o en su defecto recuperarse al restablecer condiciones normales.


## 4. Comunicaciones M2M

En el entorno serial del bus RS485, un maestro y varios esclavos deben poder comunicarse bajo el protocolo modbus, sin excepciones de comunicación. Se debe lograr consular los pulsos acumulador en los esclavos a traves del maestro usando la funcion 4 modbus.


La comunicación serial con el chip LoRa debe lograr configurar el chip, obtener información de la configuración y servir de compuerta para comunicarse usando LoRa.


En cuanto al Rpi, este tambien debe poder realizar las mismas funciones antes decritas con el LoRa. Además de subir información a Internet usando el métodos post.

## 5. Estrés lógico

Los equipos deben recuperarse de situaciones de estrés logico, tasa de baudios incorrecta, alta frecuencia de interrogación, sobrecarga de esclavos o registros. Baja pausa entre consultas, errores de comunicación etc.


## 6. Medición

Se debe verificar la correspondencia de la medición de energía entre la pantalla del medidor y la obtenida a través de los pulsos. Con una desviación no mayor a 0.1 KWh por semana. 

## 7. Mejoras

Durante todo el proceso anterior de debe mantener un registro de las obervaciones, errores y mejoras posibles al codigo y hardware. Tal que se puedan implementar optimización, luego de las cuales se debe repetir el proceso de validación.