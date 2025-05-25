# 情感陪伴智能体

基于AutoGen和ChromaDB构建的高级情感陪伴智能体，可以记忆用户偏好、模拟情感变化、自然发展关系亲密度，并主动与用户进行情感化交流。

## 特点

- 情感模拟：智能体拥有自己的情感状态，会随着交互自然变化
- 记忆管理：使用ChromaDB实现高效语义记忆存储和检索
- 多代理协作：基于AutoGen构建的多代理系统，各司其职
- 关系发展：模拟真实的关系亲密度发展过程
- 主动交互：智能体会在空闲时主动发起对话
- 自主联想：能够像人一样随机联想起过去的记忆

## 安装步骤

使用uv安装（推荐）：

```bash
# 安装uv (如果还没安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone https://github.com/yourusername/emotional-companion.git
cd emotional-companion

# 创建虚拟环境并安装依赖
uv venv
uv pip install -e .