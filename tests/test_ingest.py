import pandas as pd
import pytest
from ingest import LogFileError, parse_logs, ingest_logs

FIELDS = ["timestamp","source_ip","username","event_type","status","resource","message"]
def write_csv(path, rows, columns=FIELDS): pd.DataFrame(rows,columns=columns).to_csv(path,index=False)
def row(**changes):
    result=dict(timestamp="2026-09-10T10:00:00Z",source_ip="192.0.2.10",username="demo",event_type="login",status="success",resource="/home",message="fictional")
    result.update(changes);return result

def test_valid_rows_parse_and_insert(tmp_path):
    source=tmp_path/"events.csv";write_csv(source,[row()]);result=ingest_logs(source,tmp_path/"events.db");assert result["inserted"]==1 and not result["invalid"]
def test_missing_columns_rejected(tmp_path):
    source=tmp_path/"events.csv";write_csv(source,[row()],FIELDS[:-1])
    with pytest.raises(LogFileError,match="Missing required columns"):parse_logs(source)
def test_empty_and_malformed_files_reported(tmp_path):
    empty=tmp_path/"empty.csv";empty.write_text("",encoding="utf-8")
    with pytest.raises(LogFileError,match="CSV file is empty"):parse_logs(empty)
    malformed=tmp_path/"malformed.csv";malformed.write_text('timestamp,source_ip\n"unterminated',encoding="utf-8")
    with pytest.raises(LogFileError,match="Could not parse CSV"):parse_logs(malformed)
@pytest.mark.parametrize("changes,reason",[({"timestamp":"nope"},"invalid timestamp"),({"source_ip":"not-an-ip"},"invalid IP address"),({"username":""},"missing username")])
def test_invalid_fields_reported(tmp_path,changes,reason):
    source=tmp_path/"events.csv";value=row(**changes);write_csv(source,[value]);valid,invalid=parse_logs(source);assert not valid and reason in invalid[0]["reasons"]
