import React from 'react';
import "./field.css";

class Field extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: props.value || "",
      label: props.label || "",
      type: props.type || "",
      active: (props.locked && props.active) || false,
    };
  }

  updatevalue(event) {
    const label = event.target.placeholder;
    const value = event.target.value;
    this.setState({ value });
    //console.log(label + ':' + value);
    this.props.parentCallback(label,value);
  }

  render() {
    const { value, label, type, active } = this.state;
    const { locked } = this.props;
    const fieldClassName = `field ${(locked ? active : active || value) &&
      "active"} ${locked && !active && "locked"}`;

    return (
      <div className={fieldClassName}>
        <input
          value={value}
          placeholder={label}
          type={type}
          locked={locked}
          onChange={this.updatevalue.bind(this)}
          onFocus={() => this.setState({ active: true })}
          onBlur={() => this.setState({ active: false })}
        />
        <label>{label}</label>
      </div>
    );
  }
}
export default Field;
