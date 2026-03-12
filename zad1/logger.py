from datetime import datetime

def log_product(cur, action, article, name, user, details=""):

    cur.execute("""
    INSERT INTO ProductLogs
    (Action, ProductArticle, ProductName, UserName, Details, ActionTime)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        action,
        article,
        name,
        user,
        details,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))