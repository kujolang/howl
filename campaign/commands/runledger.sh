runledger finish "$id" \
  --status pass --verdict "Ready for review"

runledger report --output run-report.md
runledger verify --json
