# Importation des modules utilisés
import sqlite3
import pandas

# Création de la connexion
conn = sqlite3.connect("ClassicModel.sqlite")

# Récupération du contenu de Customers avec une requête SQL
customers = pandas.read_sql_query("SELECT * FROM Customers;", conn)
print(customers)

# 1 Lister les clients n’ayant jamais effecuté une commande ;
ocom = pandas.read_sql_query( """SELECT customerName  FROM Customers c
    left join Orders o
    on c.customerNumber=o.customerNumber
    WHERE o.orderNumber is null ;
    """, conn)
print(ocom)

# 2 Pour chaque employé, le nombre de clients, le nombre de commandes et le montant total de celles-ci ;
emp = pandas.read_sql_query( """
    SELECT employeeNumber, lastName, COUNT(distinct c.customerNumber), COUNT(distinct o.orderNumber),SUM(od.priceEach*quantityOrdered) FROM Employees e 
    left join Customers c
    on e.employeeNumber=c.salesRepEmployeeNumber
    left join Orders o
    on c.customerNumber=o.customerNumber
    left join OrderDetails od
    on o.orderNumber=od.orderNumber 
    group by lastName, employeeNumber ;
    """, conn)
print(emp)

#3 Idem pour chaque bureau (nombre de clients, nombre de commandes et montant total), avec en plus le nombre de clients d’un pays différent, s’il y en a ;

off = pandas.read_sql_query( """
    SELECT distinct of.country, of.officeCode,of.city, count(distinct c.customerNumber), count(distinct o.orderNumber), SUM(od.priceEach)
    FROM Offices of
    left join Employees e 
    on of.officeCode = e.officeCode
    left join Customers c
    on e.employeeNumber=c.salesRepEmployeeNumber
    left join Orders o
    on c.customerNumber=o.customerNumber
    left join OrderDetails od
    on o.orderNumber=od.orderNumber 
    group by of.officeCode, of.city, of.country;
    """, conn)
print(off)

#4 Pour chaque produit, donner le nombre de commandes, la quantité totale commandée, et le nombre de clients différents ;

prod = pandas.read_sql_query( """
    SELECT p.productCode,productName, count(o.orderNumber),sum(quantityOrdered), count(distinct c.customerNumber)
    FROM Products p
    left join OrderDetails od 
    on p.productCode = od.productCode
    left join Orders o
    on od.orderNumber=o.orderNumber
    left join Customers c
    on o.customerNumber=c.customerNumber
    group by productName, p.productCode;
    """, conn)
print(prod)

#5 Donner le nombre de commande pour chaque pays du client, ainsi que le montant total des commandes et le montant total payé : on veut conserver les clients n’ayant jamais commandé dans le résultat final ;

compays = pandas.read_sql_query( """
    SELECT c.country, count(distinct o.orderNumber) as nombredecom, sum(od.priceEach) as montantdescom, sum(pa.amount) as montantpayé
    FROM OrderDetails od 
    left join Orders o
    on od.orderNumber=o.orderNumber
    left join Customers c
    on o.customerNumber=c.customerNumber
    left join Payments pa
    on c.customerNumber=pa.customerNumber
    group by c.country;
    """, conn)
print(compays)

#6 On veut la table de contigence du nombre de commande entre la ligne de produits et le pays du client ;

table = pandas.read_sql_query( """
    SELECT productLine , c.country , count(distinct o.ordernumber)
    FROM Products p
    left join OrderDetails od 
    on p.productCode = od.productCode
    left join Orders o
    on od.orderNumber=o.orderNumber
    left join Customers c
    on o.customerNumber=c.customerNumber
    group by productLine,c.country ;
    """, conn)
print(table)

#7 On veut la même table croisant la ligne de produits et le pays du client, mais avec le montant total payé dans chaque cellule ;

table2 = pandas.read_sql_query( """
    SELECT productLine , c.country , sum(pa.amount) as montantpayé
    FROM Products p
    left join OrderDetails od 
    on p.productCode = od.productCode
    left join Orders o
    on od.orderNumber=o.orderNumber
    left join Customers c
    on o.customerNumber=c.customerNumber
    left join Payments pa
    on c.customerNumber=pa.customerNumber
    group by productLine,c.country ;
    """, conn)
print(table2)


#8 Donner les 10 produits pour lesquels la marge moyenne est la plus importante (cf buyPrice et priceEach) ;

top = pandas.read_sql_query( """
    SELECT productName , (od.priceEach - p.buyPrice) AS Marge
    FROM Products p
    left join OrderDetails od 
    on p.productCode = od.productCode
    group by productName
    ORDER BY Marge DESC
    LIMIT 10 ;
    """, conn)
print(top)

#9 Lister les produits (avec le nom et le code du client) qui ont été vendus à perte :

perte = pandas.read_sql_query( """
    SELECT productName , c.customerName, c.customerNumber, (od.priceEach - p.buyPrice) AS Marge
    FROM Products p
    left join OrderDetails od 
    on p.productCode = od.productCode
    left join Orders o
    on od.orderNumber=o.orderNumber
    left join Customers c
    on o.customerNumber=c.customerNumber
    WHERE Marge < 0
    group by productName
    ;
    """, conn)
print(perte)

#Si un produit a été dans cette situation plusieurs fois, il doit apparaître plusieurs fois,
# Une vente à perte arrive quand le prix de vente est inférieur au prix d’achat ;



#10 (bonus) Lister les clients pour lesquels le montant total payé est supérieur aux montants totals des achats ;

top = pandas.read_sql_query( """
    SELECT c.customerName as client
    FROM Products p
    left join OrderDetails od 
    on p.productCode = od.productCode
    left join Orders o
    on od.orderNumber=o.orderNumber
    left join Customers c
    on o.customerNumber=c.customerNumber
    left join Payments pa
    on c.customerNumber=pa.customerNumber
    where (amount>od.priceEach*quantityOrdered)
    group by customerName
    ;
    """, conn)
print(top)



# Fermeture de la connexion : IMPORTANT à faire dans un cadre professionnel
conn.close()
