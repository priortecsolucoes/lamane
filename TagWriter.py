from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

VALID_ACCESS_KEY = 0112358  # Use uma variável de ambiente ou um valor fixo

class WriteTagRequest(BaseModel):
    tagName: str
    stringValue: str
    intValue: int
    doubleValue: float
    accessKey: int  

class TagService:
    @staticmethod
    def getDbConnection():
        return psycopg2.connect(
            host= 'postgres.railway.internal',
            database= 'railway',
            user= 'postgres',
            password= 'HxtWVwDYJEIIcUgYUQAKlllcudMUWbax',
            port= 5432
        )
    @staticmethod
    def validateAccessKey(accessKey):
        if accessKey != VALID_ACCESS_KEY:
            raise HTTPException(status_code=403, detail="Access denied: Invalid access key")

    @staticmethod
    def updateTag(request: WriteTagRequest):
        TagService.validateAccessKey(request.accessKey) # Valida a accessKey antes de qualquer operacao
        try:
            conn = TagService.getDbConnection()
            cursor = conn.cursor()
            
            # Verifica se a tag existe
            selectTagQuery = "SELECT id FROM tag WHERE name = %s"
            cursor.execute(selectTagQuery, (request.tagName,))
            tagId = cursor.fetchone()
            if tagId:
                tagId = tagId[0]

                # Verifica se ja existem valores para a tag
                checkValueQuery = "SELECT * FROM tag_value WHERE tag_id = %s"
                cursor.execute(checkValueQuery, (tagId,))
                existingValue = cursor.fetchone()

                if existingValue:
                    updateQuery = """
                    UPDATE tag_value
                    SET string_value = %s, int_value = %s, double_value = %s
                    WHERE tag_id = %s
                    """
                    cursor.execute(updateQuery, (
                        request.stringValue, 
                        request.intValue, 
                        request.doubleValue, 
                        tagId
                    ))
                else:# Insere o primeiro valor caso nao exista
                    insertValueQuery = """
                    INSERT INTO tag_value (tag_id, string_value, int_value, double_value)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insertValueQuery, (
                        tagId, 
                        request.stringValue, 
                        request.intValue, 
                        request.doubleValue
                    ))
                conn.commit()
                message = "Tag atualizada com sucesso"
            else:
                message = "Tag não encontrada. Nenhuma ação foi realizada."
            cursor.close()
            conn.close()
            return {"message": message}
        except Exception as e:
            return {"message": f"Erro ao tentar realizar escrita de tag: {e}"}


@app.put("/update-tag")
def writeTag(request: WriteTagRequest):
    print("Recebida solicitação de update:", request)
    return TagService.updateTag(request)
