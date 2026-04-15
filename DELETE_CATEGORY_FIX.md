# DELETE Category API - Idempotency Fix

## Summary
Fixed the DELETE category endpoint to be idempotent, returning HTTP 204 No Content whether or not the category exists.

## Changes Made

### 1. Added DELETE endpoint to `controllers/category_controller.py`
- **Route**: `DELETE /categories/{category_id}`
- **Status Code**: `204 No Content`
- **Behavior**: 
  - If category exists: deletes it and returns 204
  - If category does not exist: still returns 204 (idempotent)
  - No HTTPException thrown for missing resource
- **Authorization**: Requires staff or owner role

### 2. Updated tests in `tests/unit/test_category_controller.py`
Added two new test cases:

- **test_delete_category_existing_returns_204**: 
  - Tests deletion of an existing category
  - Verifies the category is deleted from DB
  - Verifies response is None (translates to 204)

- **test_delete_category_nonexistent_returns_204**:
  - Tests deletion of non-existent category
  - Verifies no deletion attempt is made
  - Verifies response is still None (204)
  - Ensures idempotency

## Implementation Details

```python
@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["staff", "owner"])

    category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if category:
        db.delete(category)
        db.commit()

    return None
```

## Compliance with REST Standards
✅ DELETE is now idempotent (RFC 7231)
✅ Repeated calls return the same status code (204)
✅ No client-side error handling required for missing resources
✅ Aligns with best practices (e.g., AWS, Google Cloud APIs)

## Testing
Run tests with:
```bash
pytest tests/unit/test_category_controller.py -v
```

Expected results:
- All 5 tests pass (3 original + 2 new)
- New tests specifically verify idempotency behavior
