import sqlite3
import os

# --- 配置 ---
db_file_path = 'test_memory_db/chroma.sqlite3' # <--- 请确保这是你正确的路径
target_collection_name = 'episodic_memory'   # <--- 你想要查询的集合名称
# ----------------

def print_table_structure(cursor, table_name):
    print(f"\n'{table_name}' 表的结构 (列信息):")
    try:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        if not columns:
            print(f"无法获取表 '{table_name}' 的结构，或者表为空/不存在。")
            return False, []
        column_names = [col[1] for col in columns]
        for column_info in columns:
            print(column_info)
        return True, column_names
    except sqlite3.OperationalError as e:
        print(f"获取表 '{table_name}' 结构时出错: {e}")
        return False, []

def query_collection_content():
    if not os.path.exists(db_file_path):
        print(f"错误：数据库文件未找到于路径: {db_file_path}")
        return

    collection_id_str = None # String UUID from collections table
    conn = None

    try:
        conn = sqlite3.connect(f'file:{db_file_path}?mode=ro', uri=True)
        cursor = conn.cursor()
        print(f"成功连接到数据库: {db_file_path}")
        print(f"准备查询集合 '{target_collection_name}' 的内容...")

        # 1. 从 'collections' 表获取集合 ID (string UUID)
        cursor.execute("SELECT id FROM collections WHERE name = ?;", (target_collection_name,))
        result = cursor.fetchone()

        if result:
            collection_id_str = result[0]
            print(f"\n找到集合 '{target_collection_name}'，其内部 ID (UUID) 为: {collection_id_str}")
        else:
            print(f"\n错误：在数据库中未找到名为 '{target_collection_name}' 的集合。")
            # ... (之前的错误处理代码保持不变) ...
            return

        # 2. 查询 'segments' 表获取该集合的 segment_id 列表
        print(f"\n--- 查询 'segments' 表以获取 '{target_collection_name}' (Collection UUID: {collection_id_str}) 的 Segment ID ---")
        structure_exists, _ = print_table_structure(cursor, 'segments')
        if not structure_exists: return

        cursor.execute("SELECT id FROM segments WHERE collection = ?;", (collection_id_str,))
        segment_ids_tuples = cursor.fetchall()
        segment_ids = [row[0] for row in segment_ids_tuples]

        if not segment_ids:
            print(f"集合 '{target_collection_name}' 在 'segments' 表中没有找到任何 Segments。")
        else:
            print(f"找到 {len(segment_ids)} 个与此集合关联的 Segment ID(s): {segment_ids[:5]} (最多显示5个)")

        # 3. 查询 'embeddings' 表中该集合的条目 (使用 segment_ids)
        #    并获取每条 embedding 记录的整数主键 'id'
        print(f"\n--- 查询 '{target_collection_name}' 在 'embeddings' 表中的数据 (通过 Segment ID) ---")
        structure_exists, embedding_columns = print_table_structure(cursor, 'embeddings')
        embedding_integer_ids = [] # 用来存储 embeddings 表的整数主键

        if not structure_exists or 'segment_id' not in embedding_columns or 'id' not in embedding_columns:
            print("无法获取 'embeddings' 表结构或缺少必要的 'id'/'segment_id' 列，跳过查询。")
            embeddings_count = 0
        elif not segment_ids:
            print("没有 Segment ID 可供查询 'embeddings' 表。")
            embeddings_count = 0
        else:
            placeholders = ', '.join('?' for _ in segment_ids)
            # 获取整数主键 'id' 和其他信息
            query = f"SELECT id, segment_id, embedding_id, seq_id, created_at FROM embeddings WHERE segment_id IN ({placeholders});"
            cursor.execute(query, segment_ids)
            found_embeddings = cursor.fetchall()
            embeddings_count = len(found_embeddings)
            print(f"\n在 'embeddings' 表中找到与这些 Segments 关联的条目总数: {embeddings_count}")

            if embeddings_count > 0:
                print(f"\n'embeddings' 表中与这些 Segments 关联的示例数据 (每条记录的第一个值是其整数主键 'id'):")
                col_names_display = ['id(int_pk)', 'segment_id', 'embedding_id(str)', 'seq_id', 'created_at'] # 手动对应
                print(f"列名: {col_names_display}")
                for i, row in enumerate(found_embeddings[:5]): # 最多显示5条
                    print(f"示例 {i+1}: {row}")
                    embedding_integer_ids.append(row[0]) # row[0] 是整数主键 'id'
            elif segment_ids:
                 print("这些 Segments 在 'embeddings' 表中没有对应的向量数据。")
        
        if not embedding_integer_ids:
            print("\n未能从 'embeddings' 表获取任何记录的整数主键ID，无法查询元数据。")


        # 4. 查询 'embedding_metadata' 表中该集合的条目
        #    使用从 'embeddings' 表获取的整数主键 'id' 进行关联
        print(f"\n--- 查询 '{target_collection_name}' 在 'embedding_metadata' 表中的数据 ---")
        structure_exists, metadata_columns = print_table_structure(cursor, 'embedding_metadata')
        metadata_found_count = 0

        if not structure_exists or 'id' not in metadata_columns or 'key' not in metadata_columns or 'string_value' not in metadata_columns:
            print("无法获取 'embedding_metadata' 表结构或缺少必要的 'id'/'key'/'string_value' 列，跳过查询。")
        elif not embedding_integer_ids:
            print("没有来自 'embeddings' 表的整数主键ID可用于查询元数据。")
        else:
            print(f"将使用以下来自 'embeddings' 表的整数主键ID查询元数据: {embedding_integer_ids}")
            placeholders = ', '.join('?' for _ in embedding_integer_ids)
            
            # 查询所有相关的元数据条目
            query = f"SELECT id, key, string_value, int_value, float_value, bool_value FROM embedding_metadata WHERE id IN ({placeholders}) ORDER BY id, key;"
            cursor.execute(query, embedding_integer_ids)
            all_metadata_entries = cursor.fetchall()
            metadata_found_count = len(all_metadata_entries)

            print(f"\n在 'embedding_metadata' 表中找到与这些 Embedding 记录关联的元数据条目总数: {metadata_found_count}")

            if metadata_found_count > 0:
                print(f"\n'embedding_metadata' 表中关联的元数据详情:")
                current_embedding_int_id = None
                for row in all_metadata_entries:
                    emb_int_id, key, str_val, int_val, float_val, bool_val = row
                    if emb_int_id != current_embedding_int_id:
                        print(f"\n  --- 元数据 for embedding (整数主键 id FROM embeddings table): {emb_int_id} ---")
                        current_embedding_int_id = emb_int_id
                    
                    value_display = str_val  # 默认显示字符串值
                    if str_val is None: # 如果字符串值为空，尝试显示其他类型的值
                        if int_val is not None: value_display = f"(int) {int_val}"
                        elif float_val is not None: value_display = f"(float) {float_val}"
                        elif bool_val is not None: value_display = f"(bool) {bool_val}"
                        else: value_display = "NULL"
                    
                    print(f"    Key: '{key}', Value: '{value_display}'")
                    
                    # 特别指出可能的文档内容
                    if key == "$document": # ChromaDB 默认的文档键
                        print(f"      ==> 可能是文档内容: '{str_val}'")
                    elif "document" in key.lower() and str_val: # 其他可能的文档键
                         print(f"      ==> 可能是文档内容 (key: '{key}'): '{str_val}'")

            elif embedding_integer_ids: # 有整数ID但没找到元数据
                print("虽然找到了 Embedding 记录，但在 'embedding_metadata' 表中没有找到对应的元数据。")

    except sqlite3.OperationalError as e:
        # ... (之前的错误处理代码保持不变) ...
        print(f"操作数据库时发生错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")
    finally:
        if conn:
            conn.close()
            print("\n数据库连接已关闭。")

if __name__ == '__main__':
    query_collection_content()