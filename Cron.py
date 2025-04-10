import time
from datetime import datetime, date
import requests
from collections import Counter
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import pytz
class Cron:
    def __init__(self):
      print("Iniciando")
    def updateTagHistoryValue(self, tagName, doubleValue, companyPdvNumber): 
        try:
            horario = self.setLastRunTime()
            url = "https://lamanetagwriter-production.up.railway.app/update-tag-history" 
            headers = {"Content-Type": "application/json"}
            
            body = {
                "tagName": tagName,
                "companyId": companyPdvNumber,
                "stringValue": "SOCO.",
                "intValue": 0,
                "doubleValue": doubleValue, # aqui!
                "accessKey": '112358'
            }
            response = requests.put(url, json=body, headers=headers)
            if response.status_code == 200:
                print(f"✅ Tag '{tagName}' atualizada com sucesso! Valor: {doubleValue}")
            else:
                print(f"❌ Erro ao atualizar a tag '{tagName}'. Código: {response.status_code}, Resposta: {response.text}")
        except requests.RequestException as e:
            print(f"❌ Erro na requisição para atualizar a tag '{tagName}': {e}")
        except Exception as e:
            print(f"❌ Erro inesperado ao atualizar a tag '{tagName}': {e}")

    def requestWithRetries(self, url, maxRetries=2):#Faz uma requisicao com tentativas em caso de excecao
        attempt = 0
        while attempt <= maxRetries:
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()  # Levanta exceção para erros HTTP
                return response
            except requests.HTTPError as e:
                print(f"⚠️ Erro HTTP na tentativa {attempt + 1}: {e.response.status_code} - {e.response.text}")
            except requests.RequestException as e:
                print(f"⚠️ Erro na requisição na tentativa {attempt + 1}: {e}")
            except Exception as e:
                print(f"⚠️ Erro inesperado na tentativa {attempt + 1}: {e}")
            attempt += 1
            if attempt > maxRetries:
                print("❌ Todas as tentativas falharam. Verifique sua conexão ou os detalhes da API.")
                return None
            time.sleep(5)  # Aguarda 5 segundos antes de tentar novamente
    def loadData(self, data):
        keywords = [(str(row["CIDADE"]) + " " + str(row["PDV"])).upper() for _, row in data.iterrows()] 

        for index, row in data.iterrows():
            companyPdvNumber = str(row["PDV"])  # Converter para string para garantir a concatenação
            cidade = str(row["CIDADE"])
            local = str(row["LOCAL DO PDV"])
            total = row["REALIZADO"]
            extractedValue = (cidade + " " + companyPdvNumber).upper()

            if extractedValue in keywords:# Se o extractedValue estiver na lista de keywords, chama a função
                print(f"Encontrado: {extractedValue}")
                self.insertIntoDB(companyPdvNumber, cidade, local, total)
    def insertIntoDB(self, companyPdvNumber, cidade, local, total): # Aqui você implementa a inserção no banco de dados
        print(f"Inserindo no banco: PDV={companyPdvNumber}, Cidade={cidade}, Local={local}, Total={total}")###################################################################  meta ideal e 100 e meta parcial e 95
        self.updateTagHistoryValue("INDICADOR_ALCANCE_PEF_VALOR", total, companyPdvNumber)
        if total >= 100:
            self.updateTagHistoryValue("INDICADOR_ALCANCE_META_PEF_PONTUACAO", 70, companyPdvNumber)
        if total>= 95 and total < 100:
            self.updateTagHistoryValue("INDICADOR_ALCANCE_META_PEF_PONTUACAO", 35, companyPdvNumber) 
        if total < 95:
            self.updateTagHistoryValue("INDICADOR_ALCANCE_META_PEF_PONTUACAO", 10, companyPdvNumber) 
    def setLastRunTime(self):
        timeZone = pytz.timezone('America/Sao_Paulo') #Definindo o fuso horario de brasilia, nao esta errado, realmente se orienta por SP
        dateTimeBrasilia = datetime.now(timeZone)
        updatedDateandTime =dateTimeBrasilia.strftime('%d/%m/%Y %H:%M:%S')
        return updatedDateandTime


