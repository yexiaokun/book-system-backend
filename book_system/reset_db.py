# reset_db.py
from sqlmodel import SQLModel
from database import engine
# ⚠️ 必须导入 models，否则 SQLModel 不知道有哪些表要删/建
import models 

def reset_database():
    print("🧨 正在删除旧表...")
    # 这句话会删除所有继承自 SQLModel 的表 (Book)
    SQLModel.metadata.drop_all(engine) 
    
    print("🏗️ 正在重建新表...")
    # 按最新的代码重新建表
    SQLModel.metadata.create_all(engine)
    
    print("✅ 重置完成！数据已清空，表结构已更新。")

if __name__ == "__main__":
    reset_database()