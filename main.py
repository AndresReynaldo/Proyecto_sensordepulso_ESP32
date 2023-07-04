from max30102 import MAX30102
from machine import SoftI2C, Pin, PWM 
import time
from utime import ticks_diff, ticks_us, ticks_ms
#UNIVERSIDAD NACIONAL MAYOR DE SAN MARCOS
# PROYECTO PDS: SENSOR DE PULSO, GRUPO 8

# Indicadores
led = Pin(18, Pin.OUT)

    
# Habilitación de SDA(System data) y SCL(System clock)
i2c = SoftI2C(sda=Pin(21),scl=Pin(22),freq=400000)

# Variable del sensor
sensor = MAX30102(i2c=i2c)  

# Verificación de la conexión del sensor
if sensor.i2c_address not in i2c.scan():
    print("Sensor no encontrado")
    
elif not (sensor.check_part_id()):
    # Compatibilidad del sensor
    print("El sensor no es compatible")
    
else:
    print("El sensor está listo")

# Configurando el sensor a la configuración predeterminada
sensor.setup_sensor()


#--------------------------------------------------------------------------
# Apertura del archivo txt para el almacenamineto de datos 
file = open("data.txt", "w")

# Periodo de muestreo en milisegundos
periodo_muestreo = 2

#Tiempo de muestra en segundos
t_muestra = 10 #Es aproximado

contador = 0
a = (t_muestra/(periodo_muestreo*pow(10,-3)))
#---------------------------------------------------------------------------
#Definición de las variables para el cálculo del BPM
MAX_historial = 32
historial = []
latidos_historial = []
latiendo = False
latidos = 0

t_start = ticks_us()  # Empezar tiempo de recolección de datos

#Cálculo de los bpm promedio
bpm_sumatoria = 0;
bpm_datos_total = 0;
#----------------------------------------------------------------------------
inicio = time.time()


while (contador <= a):
    
    # Revisión de la entrada de datos
    sensor.check()

    # Revisión de la disponibilidad de datos 
    if sensor.available():
        # Obtención de los datos del sensor
        red_reading = sensor.pop_red_from_storage()
        ir_reading = sensor.pop_ir_from_storage()
        
        valor = red_reading
        
        #----------------------------------------------
        historial.append(valor)
       
        historial = historial[-MAX_historial:]
        minima = 0
        maxima = 0
        limite_on = 0
        limite_off = 0

        minima, maxima = min(historial), max(historial)

        limite_on = (minima + maxima * 3) // 4   # 3/4
        limite_off = (minima + maxima) // 2      # 1/2
        #----------------------------------------------
        
        if valor > 1000:
            
            # Grabación de los datos del sensor
            file.write(str(valor) + "\n")
            file.flush
            #print(valor)
            
            #------------------------------------------
            if not latiendo and valor > limite_on:
                latiendo = True                    
                led.on()
       
                t_us = ticks_diff(ticks_us(), t_start)
                t_s = t_us/1000000
                f = 1/t_s
                bpm = f * 60
                if bpm < 500:
                    t_start = ticks_us()
                    latidos_historial.append(bpm)                    
                    latidos_historial = latidos_historial[-MAX_historial:] 
                    latidos = round(sum(latidos_historial)/len(latidos_historial) ,2)
                    print ("BPM: ", latidos)

                    #Recolección de datos para el bpm promedio
                    bpm_sumatoria = bpm_sumatoria + latidos
                    bpm_datos_total = bpm_datos_total + 1
             
            if latiendo and valor< limite_off:
                latiendo = False
                led.off()
            
            
            #------------------------------------------
            
        else:
            led.off()
   
            print('Sensor inactivo')

    contador = contador + 1
    time.sleep_ms(periodo_muestreo)


final = time.time()
#Cálculo BPM promedio
print("BPM PROMEDIO: ", bpm_sumatoria/bpm_datos_total)
print("Intervalo total: {:.4f}s.".format(final-inicio))
led.off()
file.close()
