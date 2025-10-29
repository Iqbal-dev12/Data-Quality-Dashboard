import pandas as pd

# Test the duplicate detection logic
def test_duplicate_logic():
    # Create test data with duplicate IDs but different other columns
    test_data = {
        'ID': [1, 2, 1, 3, 2, 4],  # IDs 1 and 2 are duplicated
        'Name': ['John', 'Jane', 'Johnny', 'Bob', 'Janet', 'Alice'],
        'Email': ['john@email.com', 'jane@email.com', 'johnny@email.com', 'bob@email.com', 'janet@email.com', 'alice@email.com'],
        'Department': ['IT', 'HR', 'Marketing', 'IT', 'Finance', 'IT']
    }
    
    df = pd.DataFrame(test_data)
    print("Original Data:")
    print(df)
    print("\n" + "="*50 + "\n")
    
    # Test 1: All columns duplicate detection (should find no duplicates)
    all_cols_dups = df.duplicated(keep=False)
    print("All columns duplicate detection:")
    print("Duplicate mask:", all_cols_dups.tolist())
    print("Duplicate rows:")
    print(df[all_cols_dups])
    print(f"Total duplicates: {all_cols_dups.sum()}")
    print("\n" + "="*50 + "\n")
    
    # Test 2: ID column only duplicate detection (should find 4 duplicates)
    id_dups = df.duplicated(subset=['ID'], keep=False)
    print("ID column only duplicate detection:")
    print("Duplicate mask:", id_dups.tolist())
    print("Duplicate rows:")
    print(df[id_dups])
    print(f"Total duplicates: {id_dups.sum()}")
    print("\n" + "="*50 + "\n")
    
    # Test 3: Show which IDs are duplicated
    print("ID value counts:")
    print(df['ID'].value_counts().sort_index())
    
    # Test 4: Demonstrate the logic matches our expectation
    print("\nExpected behavior:")
    print("- ID=1 appears in rows 0 and 2 → Both should be marked as duplicates")
    print("- ID=2 appears in rows 1 and 4 → Both should be marked as duplicates") 
    print("- ID=3 appears in row 3 only → Should NOT be marked as duplicate")
    print("- ID=4 appears in row 5 only → Should NOT be marked as duplicate")
    print(f"\nActual result: {id_dups.sum()} duplicate rows found (should be 4)")
    
    return df, id_dups

if __name__ == "__main__":
    test_duplicate_logic()
