import React from 'react';
import "./input.css";

class Input extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      value: props.value || "",
      error: props.error || "",
      label: props.label || "Label",
      type: props.type || "text",
      id: props.id || "",
      name: props.name || "",
    };
  }

  render() {
    const { active, value, error, label, type, id, name } = this.state;
    const { predicted, locked } = this.props;
    const fieldClassName = `field ${(locked ? active : active || value) &&
      "active"} ${locked && !active && "locked"}`;

    return (
      <div className={fieldClassName}>
         <input
          id={id}
          name={name}
          type={type}
          value={value}
          placeholder={label}
          onChange={onchange}
          onFocus={() => this.setState({ active: true })}
          onBlur={() => this.setState({ active: false })}
        />
        <label htmlFor={id}>
          {label}
        </label>
      </div>
    );
  }
}

export default Input;
