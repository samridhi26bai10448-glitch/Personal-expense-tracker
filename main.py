
from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Expense Tracker")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: str
    date: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )



@app.post("/expenses")
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    new_expense = models.Expense(
    amount=expense.amount,
    category=expense.category,
    description=expense.description,
    date=expense.date
)
    

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return {
        "message": "Expense added successfully!",
        "expense": {
            "id": new_expense.id,
            "amount": new_expense.amount,
            "category": new_expense.category,
            "description": new_expense.description,
            "date": new_expense.date
        }
    }


@app.get("/expenses")
def get_expenses(db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).all()

    return {
        "expenses": [
            {
                "id": expense.id,
                "amount": expense.amount,
                "category": expense.category,
                "description": expense.description,
                "date": expense.date
            }
            for expense in expenses
        ]
    }

@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db)
):
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id
    ).first()

    if expense is None:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    db.delete(expense)
    db.commit()

    return {
        "message": "Expense deleted successfully!",
        "id": expense_id
    }
@app.put("/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    updated_expense: ExpenseCreate,
    db: Session = Depends(get_db)
):
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id
    ).first()

    if expense is None:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    expense.amount = updated_expense.amount
    expense.category = updated_expense.category
    expense.description = updated_expense.description
    expense.date = updated_expense.date

    db.commit()
    db.refresh(expense)

    return {
        "message": "Expense updated successfully!",
        "expense": {
            "id": expense.id,
            "amount": expense.amount,
            "category": expense.category,
            "description": expense.description,
            "date": expense.date
        }
    }
@app.get("/expenses/summary")
def expense_summary(db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).all()

    total_spending = sum(expense.amount for expense in expenses)

    category_totals = {}
    for expense in expenses:
        category_totals[expense.category] = (
            category_totals.get(expense.category, 0) + expense.amount
        )

    return {
        "total_expenses": len(expenses),
        "total_spending": total_spending,
        "category_wise_spending": category_totals
    }
@app.get("/expenses/monthly/{year}/{month}")
def monthly_expense_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    if month < 1 or month > 12:
        raise HTTPException(
            status_code=400,
            detail="Month must be between 1 and 12"
        )

    month_prefix = f"{year:04d}-{month:02d}"

    expenses = db.query(models.Expense).filter(
        models.Expense.date.startswith(month_prefix)
    ).all()

    total_spending = sum(expense.amount for expense in expenses)

    return {
        "year": year,
        "month": month,
        "total_expenses": len(expenses),
        "total_spending": total_spending,
        "expenses": [
            {
                "id": expense.id,
                "amount": expense.amount,
                "category": expense.category,
                "description": expense.description,
                "date": expense.date
            }
            for expense in expenses
        ]
    }
