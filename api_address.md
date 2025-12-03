# API 接口文档

### 接口列表
| 接口名称          | 请求方法 | 路径                             | 说明     |
|---------------|------|--------------------------------|--------|
| search        | POST | `/{data_source}/search`        | 查询接口   |
| verify        | POST | `/{data_source}/verify`        | 验价接口   |
| booking       | POST | `/{data_source}/booking`       | 生单接口   |
| order_detail  | POST | `/{data_source}/order_detail`  | 订单详情   |
| exchange_rate | POST | `/{data_source}/exchange_rate` | 汇率接口   |
| pay/ticket    | POST | `/{data_source}/pay`           | 支付/开票  |
| cancel        | POST | `/{data_source}/cancel`        | 取消 PNR |
| refund        | POST | `/{data_source}/refund`        | 退票接口   |
| flight_change | POST | `/{data_source}/flight_change` | 航变接收   |

---
## CAweb:CA官网接口
- **Address**: 服务器地址
- **Port**: 端口号
---