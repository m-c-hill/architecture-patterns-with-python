import model
import repository

from sqlalchemy import text


# ===================================================
#  Helper functions
# ===================================================


def insert_order_line(session):
    session.execute(
        text("INSERT INTO order_lines (order_id, sku, quantity)"
        ' VALUES ("order1", "brown-sofa", 12)')
    )
    [[orderline_id]] = session.execute(
        text("SELECT id FROM order_lines WHERE order_id=:order_id AND sku=:sku"),
        dict(order_id="order1", sku="brown-sofa"),
    )
    return orderline_id


def insert_batch(session, batch_id):
    session.execute(
        text("INSERT INTO batches (reference, sku, _total_quantity, eta)"
        ' VALUES (:batch_id, "brown-sofa", 100, null)'),
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(
        text('SELECT id FROM batches WHERE reference=:batch_id AND sku="brown-sofa"'),
        dict(batch_id=batch_id),
    )
    return batch_id


def insert_allocation(session, orderline_id, batch_id):
    session.execute(
        text("INSERT INTO allocations (orderline_id, batch_id)"
        " VALUES (:orderline_id, :batch_id)"),
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


# ===================================================
#  Tests
# ===================================================


def test_repository_can_save_a_batch(session):
    """
    Assert that a repository can be used to save a batch to a session
    """
    # Create a batch
    batch = model.Batch("batch1", "red-soap-dish", 100, eta=None)

    # Initialise the repo with the session and use it to insert a batch
    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)

    # The commit is kept outside of the repository and is the responsibility of the caller
    session.commit()

    # Use raw SQL to verify the that the correct data was saved
    rows = list(
        session.execute(text("SELECT reference, sku, _total_quantity, eta FROM batches"))
    )

    assert rows == [("batch1", "red-soap-dish", 100, None)]


def test_repository_can_retrieve_a_batch_with_allocations(session):
    """
    Assert that batches and allocations can be retrieved as expected
    """
    # Prepare the data using helper functions by inserting order lines, batches and an allocation
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    # Initialise the repo and retrieve batch1
    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    # Assert that the retrieved batch has the expected values and allocated order_lines
    expected = model.Batch("batch1", "brown-sofa", 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ only compares reference
    assert retrieved.sku == expected.sku
    assert retrieved._total_quantity == expected._total_quantity
    assert retrieved._allocations == {
        model.OrderLine("order1", "brown-sofa", 12),
    }
