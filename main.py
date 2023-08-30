# 1. Create an App that shows the dashboard page in UI. You make skip the UI if you want. The  format of the page is attached 
# 2. Sample data is attached in excel. 
# 3. Create a Fast API backend and database that can use the data and provide an API output for the UI to consume in the charts.


import uvicorn
from fastapi import FastAPI, Depends
from database import SessionLocal, engine
from sqlalchemy.orm import Session

from sqlalchemy import text
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"go to ": "http://127.0.0.1:8000/docs"}

@app.get("/get_all_data")
def get_all_data(db: Session = Depends(get_db)):
    query = text("SELECT * FROM TableData;")
    result = db.execute(query)
    data = result.fetchall()
    print(data)

    processed_data = [
        (str(item[0]), item[1], item[2], item[3], item[4], item[5], item[6])
        for item in data
    ]

    try:
        json_data = jsonable_encoder(processed_data)
        return json_data
    except ValueError as e:
        return {"error": str(e)}

@app.get("/get_new_npa_accounts")
def get_new_npa_accounts(db: Session = Depends(get_db)):
    query = text("SELECT customer_name,days_overdue,amount_outstanding FROM TableData WHERE chart_type = 'New NPA Accounts';")
    result = db.execute(query)
    data = result.fetchall()
    print(data)

    processed_data = [
        (str(item[0]), item[1], item[2])
        for item in data
    ]

    try:
        json_data = jsonable_encoder(processed_data)
        return json_data
    except ValueError as e:
        return {"error": str(e)}

@app.get("/get_new_accounts_with_recovery")
def get_new_accounts_with_recovery(db: Session = Depends(get_db)):
    query = text("SELECT customer_name,recovery,amount_outstanding FROM TableData WHERE chart_type = 'NPA Accounts with recovery';")
    result = db.execute(query)
    data = result.fetchall()
    print(data)
    processed_data = [
        (str(item[0]), item[1], item[2])
        for item in data
    ]

    try:
        json_data = jsonable_encoder(processed_data)
        return json_data
    except ValueError as e:
        return {"error": str(e)}
    
@app.get("/get_new_sma_accounts")
def get_new_sma_accounts(db: Session = Depends(get_db)):
    query = text("SELECT customer_name,days_overdue,amount_outstanding FROM TableData WHERE chart_type = 'New SMA Accounts';")
    result = db.execute(query)
    data = result.fetchall()
    print(data)

    processed_data = [
        (str(item[0]), item[1], item[2])
        for item in data
    ]

    try:
        json_data = jsonable_encoder(processed_data)
        return json_data
    except ValueError as e:
        return {"error": str(e)}


# assuming charts display the number of new accounts/recoveries per month
@app.get("/get_sma_by_month")
def get_sma_accounts_by_months(db: Session = Depends(get_db)):
    query = text("SELECT DATE_TRUNC('month', date) AS month, COUNT(customer_name) AS count FROM TableData WHERE chart_type = 'New SMA Accounts' GROUP BY month ORDER BY month;")
    result = db.execute(query)
    data = result.fetchall()

 
    processed_data = [
        {"month": item[0].strftime("%Y-%m"), "count": item[1]}
        for item in data
    ]

    return processed_data

@app.get("/get_recoveries_by_month")
def get_recoveries_by_months(db: Session = Depends(get_db)):
    query = text("SELECT DATE_TRUNC('month', date) AS month, COUNT(customer_name) AS count FROM TableData WHERE chart_type = 'NPA Accounts with recovery' GROUP BY month ORDER BY month;")
    result = db.execute(query)
    data = result.fetchall()

 
    processed_data = [
        {"month": item[0].strftime("%Y-%m"), "count": item[1]}
        for item in data
    ]

    return processed_data

@app.get("/get_npa_by_month")
def get_npa_accounts_by_months(db: Session = Depends(get_db)):
    query = text("SELECT DATE_TRUNC('month', date) AS month, COUNT(customer_name) AS count FROM TableData WHERE chart_type = 'New NPA Accounts' GROUP BY month ORDER BY month;")
    result = db.execute(query)
    data = result.fetchall()

 
    processed_data = [
        {"month": item[0].strftime("%Y-%m"), "count": item[1]}
        for item in data
    ]

    return processed_data



#considering sma1- special mention accounts- is overdues between 31 to 60days
@app.get("/get_sma1_accounts")
def get_sma1_accounts(db: Session = Depends(get_db)):
    query = text("SELECT COUNT(customer_id) as count, SUM(amount_outstanding) as total_amount FROM TableData WHERE chart_type = 'New SMA Accounts' AND days_overdue BETWEEN 31 AND 60;")
    result = db.execute(query)
    data = result.fetchall()
    print(data)

    processed_data = [
        # (str(item[0]), item[1])
        {"count": str(item[0]), "total_outstanding_amount": item[1]}
        for item in data
    ]

    try:
        json_data = jsonable_encoder(processed_data)
        return json_data
    except ValueError as e:
        return {"error": str(e)}
    
# sma2 - 61 to 90 days
@app.get("/get_sma2_accounts")
def get_sma2_accounts(db: Session = Depends(get_db)):
    query = text("SELECT COUNT(customer_id) as count, SUM(amount_outstanding) as total_amount FROM TableData WHERE chart_type = 'New SMA Accounts' AND days_overdue BETWEEN 61 AND 90;;")
    result = db.execute(query)
    data = result.fetchall()
    print(data)

    processed_data = [
        # (str(item[0]), item[1])
        {"count": str(item[0]), "total_outstanding_amount": item[1]}
        for item in data
    ]

    try:
        json_data = jsonable_encoder(processed_data)
        return json_data
    except ValueError as e:
        return {"error": str(e)}


@app.get("/recovery_percentage")
def recovery_percentage(db: Session = Depends(get_db)):
    query = text("SELECT SUM(recovery) FROM TableData WHERE chart_type = 'NPA Accounts with recovery';")
    result = db.execute(query)
    sum_recovery = result.fetchone()[0]
    print(sum_recovery)
    query = text("SELECT SUM(amount_outstanding) FROM TableData WHERE chart_type = 'NPA Accounts with recovery';")
    result = db.execute(query)
    sum_total_amount_outstanding = result.fetchone()[0]

    recovery = (sum_recovery / (sum_total_amount_outstanding +sum_recovery)) * 100
   
    return {"recoveries": recovery}

# gross non performing assets is npa/total loan given by bank (assuming total loan given is amount outstanding + recovery)
@app.get("/gross")
def gross(db: Session = Depends(get_db)):
    query = text("SELECT SUM(amount_outstanding) FROM TableData WHERE chart_type = 'New NPA Accounts';")
    result = db.execute(query)
    npa = result.fetchone()[0]
    print(npa)
    query = text("SELECT SUM(amount_outstanding) FROM TableData WHERE chart_type != 'NPA Accounts with recovery';")
    result = db.execute(query)
    npa_rcovery = result.fetchone()[0]
    print(npa_rcovery)
    query = text("SELECT SUM(recovery) FROM TableData WHERE chart_type = 'NPA Accounts with recovery';")
    result = db.execute(query)
    recovery = result.fetchone()[0]
    print(recovery)
    gross = npa + npa_rcovery - recovery

    print('gross : ', npa/gross)
    return {"total loan": gross}


# @app.get("/gross_npa")
# def gross_npa(db: Session = Depends(get_db)):
#     query = text("SELECT SUM(amount_outstanding) FROM TableData WHERE chart_type = 'New NPA Accounts';")
#     result = db.execute(query)
#     sum_amount_outstanding_npa  = result.fetchone()[0]

#     print(sum_amount_outstanding_npa )

#     query = text("""
#         SELECT SUM(amount_outstanding) AS sum_amount_outstanding
#         FROM (
#             SELECT DISTINCT customer_id, amount_outstanding
#             FROM TableData
#         ) AS unique_customers;
#     """)    
#     result = db.execute(query)
#     sum_total_amount_outstanding = result.fetchone()[0]

#     if sum_total_amount_outstanding > 0:
#         gross_npa_percentage = (sum_amount_outstanding_npa / sum_total_amount_outstanding) * 100
#     else:
#         gross_npa_percentage = 0

#     return {"gross_npa": gross_npa_percentage}




if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)