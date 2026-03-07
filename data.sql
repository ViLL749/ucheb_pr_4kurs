CREATE TABLE Roles (
    RoleID INTEGER PRIMARY KEY AUTOINCREMENT,
    RoleName TEXT NOT NULL
);

CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    FIO TEXT NOT NULL,
    Login TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    RoleID INTEGER,
    FOREIGN KEY (RoleID) REFERENCES Roles(RoleID)
);

CREATE TABLE Categories (
    CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    CategoryName TEXT NOT NULL
);

CREATE TABLE Manufacturers (
    ManufacturerID INTEGER PRIMARY KEY AUTOINCREMENT,
    ManufacturerName TEXT NOT NULL
);

CREATE TABLE Suppliers (
    SupplierID INTEGER PRIMARY KEY AUTOINCREMENT,
    SupplierName TEXT NOT NULL
);

-- 4. Таблица товаров
CREATE TABLE Products (
    Article TEXT PRIMARY KEY,
    ProductName TEXT NOT NULL,
    CategoryID INTEGER,
    ManufacturerID INTEGER,
    SupplierID INTEGER,
    Price DOUBLE NOT NULL,
    Discount INTEGER DEFAULT 0,
    QuantityInStock INTEGER NOT NULL,
    Description TEXT,
    Photo TEXT,
    WarrantyMonths INTEGER,
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID),
    FOREIGN KEY (ManufacturerID) REFERENCES Manufacturers(ManufacturerID),
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
);

CREATE TABLE PickupPoints (
    PointID INTEGER PRIMARY KEY AUTOINCREMENT,
    Address TEXT NOT NULL,
    WorkHours TEXT,
    Phone TEXT
);

CREATE TABLE Orders (
    OrderID TEXT PRIMARY KEY,
    OrderDate TEXT NOT NULL,
    DeliveryDate TEXT,
    PointID INTEGER,
    UserID INTEGER,
    ReceiveCode INTEGER,
    StatusID INTEGER,
    FOREIGN KEY (PointID) REFERENCES PickupPoints(PointID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (StatusID) REFERENCES Statuses(StatusID)
);

CREATE TABLE OrderItems (
    OrderItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID TEXT,
    Article TEXT,
    Quantity INTEGER NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (Article) REFERENCES Products(Article)
);


CREATE TABLE Statuses (
    StatusID INTEGER PRIMARY KEY AUTOINCREMENT,
    StatusName TEXT NOT NULL UNIQUE
);

