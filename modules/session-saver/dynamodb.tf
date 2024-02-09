resource "aws_dynamodb_table" "this" {
  name           = "sso_elevator_session_events"
  billing_mode   = "PAY_PER_REQUEST"  # You can change this to "PROVISIONED" if you want provisioned capacity
  hash_key       = "timestamp"
  attribute {
    name = "timestamp"
    type = "N"
  }
#   ttl {
#     attribute_name = "ttl"
#     enabled        = true
#   }
}