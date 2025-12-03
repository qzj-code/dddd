import time

import redis

from common.global_variable import GlobalVariable

r = redis.Redis(host=GlobalVariable.REDIS_HOST, port=GlobalVariable.REDIS_PORT,
                db=GlobalVariable.REDIS_TASK_RESULT_DB,
                password=GlobalVariable.REDIS_PASSWORD,
                decode_responses=True)

TOKEN_KEY = "dx_tokens"


def fetch_token():
    """
    立即尝试取出一个未过期的 token（每个只用一次）。
    返回 token 字符串，或者没有可用时返回 None。
    Returns:

    """
    r = redis.Redis(host=GlobalVariable.REDIS_HOST, port=GlobalVariable.REDIS_PORT,
                    db=GlobalVariable.REDIS_TASK_RESULT_DB,
                    password=GlobalVariable.REDIS_PASSWORD,
                    decode_responses=True)
    now = int(time.time())
    # 清理过期的（只做一次保持集合干净）
    # r.zremrangebyscore(TOKEN_KEY, "-inf", now - 240)
    # 原子弹出最早到期的一个 token
    print("取之前", r.zrange(TOKEN_KEY, 0, -1))

    res = r.zpopmin(TOKEN_KEY, count=1)  # 结果形如 [(token, score)] 或空
    print(res)
    if not res:
        return None
    token, expiry = res[0]
    return token


def fetch_token_blocking(timeout=5.0, backoff=0.2):
    """
        轮询拿 token，最多等 timeout 秒。失败时每次等 backoff 秒再试。
    返回 token 或 None（超时未拿到）。
    Args:
        timeout:
        backoff:

    Returns:

    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        token = fetch_token()
        if token:
            return token
        time.sleep(backoff)
    return None

# if __name__ == '__main__':
#     tok = fetch_token()
#     if tok:
#         print("拿到 token:", tok)
#     else:
#         print("当前没有可用 token，稍后重试")

# # 或者想等一会儿再拿（最多等 5 秒）
# tok = fetch_token_blocking(timeout=5)
# if tok:
#     print("拿到 token:", tok)
# else:
#     print("超时仍没拿到 token")
