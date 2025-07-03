import cv2
import numpy as np
import serial
import time


class EmotionsVisualization:
    def __init__(self, port='COM3', baudrate=9600):
        """
        Inicializa la visualización y la conexión serial con el Arduino.
        Asegúrate de cambiar 'COM3' por el puerto correcto de tu Arduino.
        Puedes encontrar el puerto en el IDE de Arduino (Herramientas -> Puerto).
        """
        self.emotion_colors = {
            'surprise': (184, 183, 83),
            'angry': (35, 50, 220),
            'disgust': (79, 164, 36),
            'sad': (186, 119, 4),
            'happy': (27, 151, 239),
            'fear': (128, 37, 146)
        }

        # --- INICIO DE LA IMPLEMENTACIÓN SERIAL ---
        self.ser = None
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Espera a que la conexión serial se establezca
            print(f"Conexión serial establecida en el puerto {port}")
        except serial.SerialException as e:
            print(f"Error: No se pudo abrir el puerto serial {port}.")
            print(f"Asegúrate de que el Arduino esté conectado y el puerto sea el correcto.")
            print(f"Error original: {e}")
        # --- FIN DE LA IMPLEMENTACIÓN SERIAL ---

        # Variable para controlar el tiempo del último envío
        self.last_sent_time = 0

    def send_emotion_to_arduino(self, emotion: str):
        """
        Envía la emoción como una cadena de texto al Arduino, pero solo si han pasado 3 segundos
        desde el último envío.
        """
        current_time = time.time()
        # Comprueba si han pasado al menos 3 segundos desde el último envío
        if current_time - self.last_sent_time >= 3:
            if self.ser and self.ser.is_open:
                try:
                    # Se envía la emoción seguida de un salto de línea '\n'
                    # para que Arduino sepa cuándo termina el mensaje.
                    self.ser.write(f"{emotion}\n".encode('utf-8'))
                    print(f"Emoción enviada a Arduino: {emotion}")
                    self.last_sent_time = current_time  # Actualiza el tiempo del último envío
                except serial.SerialException as e:
                    print(f"Error al enviar datos: {e}")
        else:
            # Opcional: Puedes imprimir un mensaje si no se envía la emoción
            # print(f"Esperando para enviar la próxima emoción. Tiempo restante: {3 - (current_time - self.last_sent_time):.2f}s")
            pass


    def main(self, emotions: dict, original_image: np.ndarray):
        # --- LÓGICA PARA ENCONTRAR Y ENVIAR LA EMOCIÓN DOMINANTE ---
        if emotions:  # Asegurarse de que el diccionario de emociones no está vacío
            # Encontrar la emoción con el puntaje más alto
            dominant_emotion = max(emotions, key=emotions.get)

            # Enviar la emoción dominante al Arduino (con el control de tiempo incorporado)
            self.send_emotion_to_arduino(dominant_emotion)

        # --- Dibuja las barras y texto en la imagen (tu código original) ---
        for i, (emotion, score) in enumerate(emotions.items()):
            cv2.putText(original_image, emotion, (10, 30 + i * 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        self.emotion_colors.get(emotion, (255, 255, 255)), 1,
                        cv2.LINE_AA)
            cv2.rectangle(original_image, (150, 15 + i * 40), (150 + int(score * 2.5), 35 + i * 40),
                          self.emotion_colors.get(emotion, (255, 255, 255)),
                          -1)
            cv2.rectangle(original_image, (150, 15 + i * 40), (400, 35 + i * 40), (255, 255, 255), 1)

        return original_image

    def close(self):
        """
        Cierra la conexión serial si está abierta.
        """
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Conexión serial cerrada.")
