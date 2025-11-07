from typing import Any, Mapping, Optional, overload
from jinja2 import Environment, FileSystemLoader, StrictUndefined
import yaml
from pathlib import Path

@overload
def _load_values(values_path: str, key: None= ...) -> Mapping[str, Any]: ...

@overload
def _load_values(values_path: str, key: str) -> Mapping[str, Any]: ...

def _load_values(
        values_path: str, 
        key: Optional[str] = None
    ) -> Mapping[str, Any]:
    
    values_path = Path(values_path)

    if not values_path.is_file():
        raise FileNotFoundError(f"values file not found: {values_path}")
    
    with values_path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    if key is None:
        return data
    elif key not in data:
        raise KeyError(f"key `{key}` is not presented.")
    else:
        return data.get(key)

def _build_env(source_path: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(source_path)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )

def _ensure_dir_exists(dir: Path):
     dir.parent.mkdir(parents=True, exist_ok=True)

def render(resource_type: str,
        source_path: str, 
        template_name: str, 
        values_path: str, 
        output_path: str
    ) -> None:

    source_path = Path(source_path)
    output_path = Path(output_path)

    env = _build_env(source_path)
    data = _load_values(values_path, resource_type)
    template = env.get_template(template_name)
    output_path = Path(f"{output_path}/{resource_type}")
    xml = []
    
    for item in data:
        xml = template.render(**item)
        output = Path(f"{output_path}/{item["name"]}.xml")
        _ensure_dir_exists(output)
        output.write_text(xml, encoding="utf-8")
        print(f"Generated {output}")    
