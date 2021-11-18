import time
import numpy as np
import cv2
import sys
from rmn import RMN
import PySimpleGUI as sg
import glob

import wintest

class SinglePlayer():
    def __init__(self):
        self.listemo = []
        self.images_list = []
        self.list = []

    def time_as_int(self):
        return int(round(time.time() * 100))


    def storeExpressions(self):
        rmn = RMN()
        self.images_list = [i for i in glob.glob("images/*.png")]                   # guarda o diretório das imagens no 'images_list'
        for imagem in self.images_list:                                            # guarda as expressões das imagens em 'list'
            image = cv2.imread(imagem)
            resultsimg = rmn.detect_emotion_for_single_frame(image)
            for resultimg in resultsimg:
                emocao = self.translateEmo(resultimg['emo_label']);
                self.list.append(resultimg['emo_label'])
                self.listemo.append(emocao)

    def retornaList(self):
        return self.list

    def translateEmo(self,emolabel):  # Traduz o emolabel para o 'OutMestre' da JANELA6 e JANELA2
        emocao = ""

        if(emolabel == 'happy'):
            emocao = "Feliz"
        elif(emolabel == 'sad'):
            emocao = "Triste"
        elif(emolabel == 'neutral'):
            emocao = "Neutro"
        elif(emolabel == 'disgust'):
            emocao = "Nojo"
        elif(emolabel == 'fear'):
            emocao = "Medo"
        elif(emolabel == 'angry'):
            emocao = "Bravo"
        elif(emolabel == 'surprise'):
            emocao = "Surpreso"

        return emocao                              

    def jogo(self,janela1, janela2, nome):
        janela1.close()
        score = 0

        rmn = RMN()

        self.storeExpressions()

        for x in range(len(self.list)):
            vid1 = cv2.VideoCapture(0)

            results = []
            result = {}

            current_time = 0
            start_time = self.time_as_int()

            while current_time <= 500:
                event, values = janela2.read(timeout=1)

                if event == sg.WIN_CLOSED:
                    janela2.close()
                    sys.exit()

                janela2['Jogador'].update(nome)
                janela2['camJogador'].update('images.utils/user.png')
                janela2['Imagem'].update('images.utils/teacher.png')
                janela2['OutImage'].update("")
                janela2['OutJogador'].update(" ")
                janela2['contador'].update('{:02d}'.format(
                    (current_time // 100) % 60))                      
                janela2['expressao'].update(
                    "Aguarde a imagem!", font=('Poppins', 28, "bold"))
                fase_str = str(x+1) + " / " + str(len(self.list))
                janela2['fase'].update(str(fase_str))
                
                current_time = self.time_as_int() - start_time

            current_time = 0
            start_time = self.time_as_int()

            while True:

                ret, frame = vid1.read()
                if frame is None or ret is not True:
                    continue

                try:

                    emoproba = 0
                    emolabel = ""
                    
                    event, values = janela2.read(timeout=1)
                    current_time = self.time_as_int() - start_time

                    janela2['Imagem'].update(filename=self.images_list[x])
                    janela2['expressao'].update(
                    "Imite a expressão!", font=('Poppins', 28, "bold"))
                    janela2['OutImage'].update(self.listemo[x], text_color="black", font=("Poppins", 25, "bold"))


                    if event == "Exit" or event == sg.WIN_CLOSED:
                        vid1.release()
                        janela2.close()
                        sys.exit()

                    frame = np.fliplr(frame).astype(np.uint8)
                    
                    if(current_time >= 100):
                        results = rmn.detect_emotion_for_single_frame(frame)

                    for result in results:
                        emolabel = result['emo_label']
                        emoproba = result['emo_proba']

                    if (emoproba > 0.7 and emolabel == self.list[x] and current_time < 1000):
                        
                        current_time = 0
                        start_time = self.time_as_int()

                        score += 1
                        while current_time <= 500:
                            event, values = janela2.read(timeout=1)

                            if event == sg.WIN_CLOSED:
                                janela2.close()
                                sys.exit()

                            current_time = self.time_as_int() - start_time

                            janela2['OutJogador'].update(
                                "Expressão Correta", text_color="#19D342", font=("Poppins", 25, "bold"))
                            janela2['scorenum'].update(value=score)

                        start_time = self.time_as_int()
                        break

                    elif (current_time > 1000):
                        current_time = 0
                        start_time = self.time_as_int()

                        while current_time <= 500:
                            event, values = janela2.read(timeout=1)

                            if event == sg.WIN_CLOSED:
                                janela2.close()
                                sys.exit()

                            current_time = self.time_as_int() - start_time

                            janela2['OutJogador'].update(
                                "Tempo Esgotado", text_color="#D4181A", font=("Poppins", 25, "bold"))

                        start_time = self.time_as_int()
                        break

                    imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                    janela2['camJogador'].update(data=imgbytes)
                    janela2['contador'].update('{:02d}:{:02d}'.format((current_time // 100) // 60,
                                                                            (current_time //
                                                                            100) % 60))
                except Exception as err:
                    print(err)
                    continue
            vid1.release()
        janela2.close()
        return score

class MultiPlayer(SinglePlayer):
   
    def nextTurn(self, user, janela2, janela6, i, n, nome="aluno"):
        current_time = 0
        start_time = self.time_as_int()

        if(user == "aluno"):
            janela6['camMestre'].update(
                filename="images.utils/teacher.png") #Atualiza a imagem na aba Mestre - (Janela Mestre)                                   
            
            janela6['expressao'].update(" ") # Limpa o campo de 'Faca uma expressão'
            janela6['mestre'].update(text_color="black", font=(
                'Poppins', 30, "bold"))                       

            while current_time <= 500: # Timer de contagem (5 segundos)
            
                event, values = janela2.read(timeout=1)

                if event == sg.WIN_CLOSED:
                    janela2.close()
                    sys.exit()

                janela2['contador'].update('{:02d}'.format( #Atualiza o tempo da Janela do Aluno
                    (current_time // 100) % 60))                       
                janela2['OutAluno'].update(" ", text_color="black", font=(
                    'Poppins', 20, "bold")) #
                janela2['expressao'].update(
                    "Atenção "+nome+", agora é a sua vez!", font=('Poppins', 28, "bold"))  

                current_time = self.time_as_int() - start_time

            janela2['expressao'].update("Faça uma Expressão!", font=('Poppins', 28, "bold"))                    
            janela2['mestre'].update(text_color="black", font=('Poppins', 20, "bold"))                       

        elif(user == "mestre"):
            while current_time <= 500: # Timer de contagem (5 segundos)                                                                    # feito
                
                event2, values2 = janela2.read(timeout=1)
                event, values = janela6.read(timeout=1)

                if event2 == sg.WIN_CLOSED or event == sg.WIN_CLOSED:
                    janela2.close()
                    janela6.close()
                    sys.exit()

                janela2['aluno'].update(nome)
                janela2['contador'].update("")
                janela2['mestre'].update(text_color="black", font=('Poppins', 30, "bold"))                   
                janela2['aluno'].update(text_color="black", font=('Poppins', 30, "bold"))                       

                janela2['expressao'].update(" ")
            
                janela2['OutMestre'].update(" ")
                janela2['OutAluno'].update("Aguarde", text_color="#D4181A", font=(
                    "Poppins", 25, "bold"))                                                               

                fase_str = str(i+1) + " / " + str(n)
                janela2['fase'].update(str(fase_str))
                janela6['fase'].update(str(fase_str))
            
                janela6['OutMestre'].update(" ")
                janela6['contador'].update('{:02d}'.format(
                    (current_time // 100) % 60))                         
                janela6['expressao'].update(
                    "Atenção Mestre, é a sua vez!", font=('Poppins', 28, "bold"))  
                janela6['camMestre'].update(filename="images.utils/teacher.png")

                current_time = self.time_as_int() - start_time
            
            janela6['expressao'].update("Mestre, faça uma Expressão!")
            janela6['mestre'].update(text_color="black", font=('Poppins', 20, "bold"))       

    def profRec(self, janela2, janela6, i, n, nome, neutral=0):  # Captura da tela do mestre
        vid = cv2.VideoCapture(0)
        maior = 0
        frame_dic = {}
        emotion = ""
        frame = ""
        img_frame = ""
        emotions = []
        emocao = ""

        rmn = RMN()

        # "Atenção Mestre, é a sua vez!",
        self.nextTurn("mestre", janela2, janela6, i, n, nome)

        current_time = 0
        start_time = self.time_as_int()

        while current_time <= 500:  # Timer 5 segundos de Captura das expressões do Mestre
            event2, values2 = janela2.read(timeout=1)
            event, values = janela6.read(timeout=1)
            janela6['contador'].update('{:02d}.{:02d}'.format(
                (current_time // 100) % 60, current_time % 100))

            ret, frame_cap = vid.read()

            if frame_cap is None or ret is not True:
                continue

            try:
                if event == sg.WIN_CLOSED or event2 == sg.WIN_CLOSED:
                    vid.release()
                    janela2.close()
                    janela6.close()
                    sys.exit()

                emoproba = 0
                emolabelProf = ""

                current_time = self.time_as_int() - start_time

                frame_cap = np.fliplr(frame_cap).astype(np.uint8)
                resultsProf = rmn.detect_emotion_for_single_frame(frame_cap)

                # Captura de emoções

                for resultProf in resultsProf:
                    emolabelProf = resultProf['emo_label']
                    emoproba = resultProf['emo_proba']

                    emocao = self.translateEmo(emolabelProf) # Traduz o emolabel

                    janela6['OutMestre'].update(
                        emocao,  text_color="black", font=("Poppins", 25, "bold"))

                # Capta as expressões diferentes de neutro e com 70% do emoproba
                if(emoproba > 0.7 and emolabelProf != "neutral"):
                    emotions.append(emolabelProf)

                    # Se o emolabel for diferente de todas as keys, incrementa no frame_dic
                    if(emolabelProf != key for key in frame_dic):
                        frame_dic[emolabelProf] = frame_cap

                imgbytes = cv2.imencode('.png', frame_cap)[1].tobytes()
                janela6['camMestre'].update(data=imgbytes)

            except Exception as err:
                print(err)
                continue

        for e in emotions: # Captura a emoção com maior frequência
            if(emotions.count(e) > maior):
                maior = emotions.count(e)
                emotion = e         # emolabel final

        # Condicional caso não tenha sido gerado emoção ou só tenha gerado neutro
        if len(emotions) <= 0 and emotion == "":
            neutral += 1

            if(neutral >= 5): # Retorna ao menu
                return -1

            current_time = 0
            start_time = self.time_as_int()

            while current_time <= 500: # Timer de delay e update
                event, values = janela6.read(timeout=1)

                if event == sg.WIN_CLOSED:
                    janela6.close()
                    sys.exit()

                janela6['camMestre'].update(filename="images.utils/teacher.png")
                janela6['OutMestre'].update(
                    "Tente Novamente", text_color="#D4181A", font=("Poppins", 25, "bold"))
                current_time = self.time_as_int() - start_time

            start_time = self.time_as_int()
            vid.release() # Interrompe a captura do RMN
            emotion = self.profRec(janela2, janela6, i, n, nome, neutral)

        emocao = self.translateEmo(emotion)

        janela2['OutMestre'].update(
            emocao, text_color="black", font=("Poppins", 25, "bold"))
        janela6['OutMestre'].update(
            emocao, text_color="black", font=("Poppins", 25, "bold"))

        # Função que capta o frame de acordo com expressão de maior frequência
        for key in frame_dic:   # Guarda a imagem do mestre
            if key == emotion:
                img_frame = cv2.imencode('.png', frame_dic[key])[1].tobytes()
                janela2['camMestre'].update(data=img_frame)
                janela6['camMestre'].update(data=img_frame)

        vid.release()
        return emotion

    def alunoRec(self,janela1, janela2, janela6, n, nome):  # Captura das expressôes do Aluno
        janela1.close()
        score = 0

        rmn = RMN()

        for i in range(int(n)): # Fases do jogo
            results = []
            result = {}

            emo_p = self.profRec(janela2, janela6, i, n, nome) # Chama a captura do Mestre

            # Caso só tenha sido gerado neutro ele retorna -1 para retornar ao menu
            if(emo_p == -1):
                janela2.close()
                janela6.close()
                return -1

            vid1 = cv2.VideoCapture(2)

            # "Atenção Aluno, é a sua vez!"
            self.nextTurn("aluno", janela2, janela6, i, n, nome)

            current_time = 0
            start_time = self.time_as_int()                                                                # ===

            while True:
                ret, frame = vid1.read()
                if frame is None or ret is not True:
                    continue

                event, values = janela2.read(timeout=1)
                event6, values6 = janela6.read(timeout=1)

                janela2['aluno'].update(
                    text_color="black", font=('Poppins', 20, "bold"))

                if event == sg.WIN_CLOSED or event6 == sg.WIN_CLOSED:
                    vid1.release()
                    janela6.close()
                    janela2.close()
                    sys.exit()

                try:
                    emoproba = 0
                    emolabel = ""

                    # Update na tela dos frames da Webcam
                    frame = np.fliplr(frame).astype(np.uint8)
                    imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                    janela2['camAluno'].update(data=imgbytes)
                    janela2['contador'].update('{:02d}.{:02d}'.format(
                        (current_time // 100) % 60, current_time % 100))

                    # Começa a captura das expressões depois de 2 segundos
                    current_time = self.time_as_int() - start_time
                    if(current_time >= 200):
                        results = rmn.detect_emotion_for_single_frame(frame)

                    for result in results:
                        emolabel = result['emo_label']
                        emoproba = result['emo_proba']

                    # Compara se as emoções são iguais
                    if (emoproba > 0.7 and emolabel == emo_p and current_time < 1000): # Se as expressões forem iguais e não tiver chegado em 10 segundos de captura

                        current_time = 0
                        start_time = self.time_as_int()

                        score += 1 # Aumenta 1 ponto
                        while current_time <= 500: # Timer de delay e update
                            event, values = janela2.read(timeout=1)

                            if event == sg.WIN_CLOSED:
                                janela2.close()
                                sys.exit()

                            current_time = self.time_as_int() - start_time

                            janela2['OutMestre'].update(
                                "Expressão Correta", text_color="white", font=("Poppins", 25, "bold"))
                            janela2['OutAluno'].update(
                                "Expressão Correta", text_color="#19D342", font=("Poppins", 25, "bold"))
                            janela2['scorenum'].update(value=score)

                        start_time = self.time_as_int()
                        break

                    elif (current_time > 1000): # Caso o tempo passe de 10 segundos

                        current_time = 0
                        start_time = self.time_as_int()

                        while current_time <= 500: # Timer de delay e update
                            event, values = janela2.read(timeout=1)
                            current_time = self.time_as_int() - start_time

                            if event == sg.WIN_CLOSED:
                                janela2.close()
                                sys.exit()

                            janela2['OutMestre'].update(
                                "Tempo Esgotado", text_color="white", font=("Poppins", 25, "bold"))
                            janela2['OutAluno'].update(
                                "Tempo Esgotado", text_color="#D4181A", font=("Poppins", 25, "bold"))

                        start_time = self.time_as_int()
                        break

                except Exception as err:
                    print(err)
                    continue
            vid1.release()
            janela2['camAluno'].update(filename="images.utils/user.png")
            janela2['camMestre'].update(filename="images.utils/teacher.png")
        janela2.close()
        janela6.close()
        return score                                                                                         # ===