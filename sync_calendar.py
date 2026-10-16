#!/usr/bin/env python3
"""Fetch the public NFF iCalendar feed and convert events to data/matches.json.

This imports calendar events only. It does not claim to provide live scores,
scorers, cards or other match incidents.
"""
from __future__ import annotations
import json
import re
import urllib.request
from datetime import datetime, date, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

URL = "https://www.fotball.no/footballapi/Calendar/GetCalendar?tournamentId=205682"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "matches.json"
OSLO = ZoneInfo("Europe/Oslo")


def unescape_ical(value: str) -> str:
    return value.replace(r'\n', '\n').replace(r'\,', ',').replace(r'\;', ';').replace(r'\\', '\\').strip()


def parse_dt(value: str, params: str):
    value = value.strip()
    if value.startswith('TZID='):
        pass
    if 'VALUE=DATE' in params or re.fullmatch(r'\d{8}', value):
        return datetime.strptime(value[:8], '%Y%m%d').replace(tzinfo=OSLO), True
    if value.endswith('Z'):
        return datetime.strptime(value, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc).astimezone(OSLO), False
    match = re.search(r'TZID=([^;:]+)', params)
    tz = ZoneInfo(match.group(1)) if match else OSLO
    for fmt in ('%Y%m%dT%H%M%S', '%Y%m%dT%H%M'):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=tz).astimezone(OSLO), False
        except ValueError:
            continue
    return None, False


def main():
    req = urllib.request.Request(URL, headers={'User-Agent': 'SunmoreLive/0.1 (calendar sync)'})
    with urllib.request.urlopen(req, timeout=25) as response:
        calendar_text = response.read().decode('utf-8-sig', errors='replace')

    # RFC 5545 line folding: a continuation line starts with space or tab.
    physical = calendar_text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    lines = []
    for line in physical:
        if line.startswith((' ', '\t')) and lines:
            lines[-1] += line[1:]
        else:
            lines.append(line)

    events, current = [], None
    for line in lines:
        if line == 'BEGIN:VEVENT':
            current = {}
        elif line == 'END:VEVENT' and current is not None:
            events.append(current)
            current = None
        elif current is not None and ':' in line:
            left, value = line.split(':', 1)
            name, *param_parts = left.split(';')
            current[name.upper()] = {'value': unescape_ical(value), 'params': ';'.join(param_parts)}

    result = []
    for i, event in enumerate(events):
        start_item = event.get('DTSTART')
        if not start_item:
            continue
        start, all_day = parse_dt(start_item['value'], start_item['params'])
        if not start:
            continue
        end_item = event.get('DTEND')
        end, _ = parse_dt(end_item['value'], end_item['params']) if end_item else (None, False)
        get = lambda key: event.get(key, {}).get('value', '')
        result.append({
            'id': get('UID') or f'nff-event-{i}-{start.isoformat()}',
            'date': start.date().isoformat(),
            'start': start.isoformat(),
            'end': end.isoformat() if end else None,
            'allDay': all_day,
            'title': get('SUMMARY') or 'Fotballkamp',
            'description': get('DESCRIPTION'),
            'location': get('LOCATION'),
            'url': get('URL') or 'https://www.fotball.no/fotballdata/turnering/hjem/?fiksId=205682&underside=kamper',
        })
    result.sort(key=lambda item: (item['date'], item['start'], item['title']))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        'source': URL,
        'tournamentId': 205682,
        'syncedAt': datetime.now(OSLO).isoformat(),
        'dataType': 'calendar-events-only',
        'events': result,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote {len(result)} calendar events to {OUT}')

if __name__ == '__main__':
    main()
