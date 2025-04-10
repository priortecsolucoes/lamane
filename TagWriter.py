from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

VALID_ACCESS_KEY = os.getenv("EXPECTED_ACCESS_KEY")

class WriteTagRequest(BaseModel):
    tagName: str
    companyId: int
    stringValue: str
    intValue: int
    doubleValue: float
    accessKey: str

class TagService:
    @staticmethod
    def getDbConnection():
        return psycopg2.connect(
            host=os.getenv('HOST'),
            database=os.getenv('DATABASE'),
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD'),
            port=os.getenv('PORT')
        )

    @staticmethod
    def validateAccessKey(accessKey):
        if accessKey != VALID_ACCESS_KEY:
            raise HTTPException(status_code=403, detail="Access denied: Invalid access key")

    @staticmethod
    def updateTag(request: WriteTagRequest):
        TagService.validateAccessKey(request.accessKey)
        try:
            conn = TagService.getDbConnection()
            cursor = conn.cursor()

            selectTagQuery = """
            SELECT id FROM company_tag 
            WHERE tag_id = (SELECT id FROM tag WHERE name = %s)
            AND company_id = (SELECT id FROM company WHERE company_pdv_number = %s)
            """
            cursor.execute(selectTagQuery, (request.tagName, request.companyId))
            companyTagId = cursor.fetchone()

            if companyTagId:
                companyTagId = companyTagId[0]

                checkValueQuery = "SELECT * FROM tag_value WHERE company_tag_id = %s"
                cursor.execute(checkValueQuery, (companyTagId,))
                existingValue = cursor.fetchone()

                if existingValue:
                    updateQuery = """
                    UPDATE tag_value
                    SET string_value = %s, int_value = %s, double_value = %s
                    WHERE company_tag_id = %s
                    """
                    cursor.execute(updateQuery, (
                        request.stringValue,
                        request.intValue,
                        request.doubleValue,
                        companyTagId
                    ))

                    conn.commit()
                    message = "Tag atualizada com sucesso"
                else:
                    message = "Tag encontrada, mas ainda não possui valores. Nenhuma ação realizada."
            else:
                message = "Tag não encontrada. Nenhuma ação foi realizada."

            cursor.close()
            conn.close()
            return {"message": message}
        except Exception as e:
            return {"message": f"Erro ao tentar realizar escrita de tag: {e}"}

    @staticmethod
    def updateTagHistoryValue(request: WriteTagRequest):
        TagService.validateAccessKey(request.accessKey)
        print("Iniciando o metodo")
        try:
            conn = TagService.getDbConnection()
            cursor = conn.cursor()
            print("Iniciou o db, iniciou o cursor")
            selectTagQuery = """
            SELECT id FROM company_tag 
            WHERE tag_id = (SELECT id FROM tag WHERE name = %s)
            AND company_id = (SELECT id FROM company WHERE company_pdv_number = %s)
            """
            cursor.execute(selectTagQuery, (request.tagName, request.companyId))
            companyTagId = cursor.fetchone()
            print(request.tagName)
            print(request.companyId)
            if companyTagId:
                companyTagId = companyTagId[0]
                print(companyTagId)
                insertHistoryQuery = """
                UPDATE tag_history_value
                    SET string_value = %s, int_value = %s, double_value = %s
                    WHERE company_tag_id = %s
                """
                cursor.execute(insertHistoryQuery, (
                    request.stringValue,
                    request.intValue,
                    request.doubleValue,
                    companyTagId
                ))

                conn.commit()
                message = "Histórico da tag atualizado com sucesso"
                print(message)
            else:
                message = "Tag não encontrada. Nenhum histórico foi registrado."
                print(message)
            cursor.close()
            conn.close()
            return {"message": message}
        except Exception as e:
            return {"message": f"Erro ao registrar histórico de tag: {e}"}


@app.put("/update-tag")
def writeTag(request: WriteTagRequest):
    return TagService.updateTag(request)

@app.put("/update-tag-history")
def writeTagHistory(request: WriteTagRequest):
    return TagService.updateTagHistoryValue(request)
