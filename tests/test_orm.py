# import models

# def test_order_line_mapper_can_load_lines(session):
#     session.execute(
#         'INSERT INTO order_lines (orderid, sku, quantity) VALUES'
#         '("order1, "RED-CHAIR", 12)'
#         '("order2, "BLUE-BOOKS", 2)'
#         '("order3, "YELLOW-RUG", 1)'
#     )
#     expected = [
#         models.OrderLine("order1", "RED-CHAIR", 12),
#         models.OrderLine("order2", "BLUE-BOOKS", 2),
#         models.OrderLine("order3", "YELLOW-RUG", 1)
#     ]
#     assert session.query(models.OrderLine).all() == expected


# def test_order_line_mapper_can_save_lines(session):
#     new_line = models.OrderLine("order1", "RED-CHAIRS", 12)
#     session.add(new_line)
#     session.commit()

#     rows = list(session.execute('SELECT orderid, sku, quantity FROM "order_lines"'))
#     assert rows == [("order1", "RED-CHAIRS", 12)]
