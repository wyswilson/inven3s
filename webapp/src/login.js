import React, { useState } from 'react';
import Input from './input.js';
import axios from 'axios';
import { setUserSession } from './utils/common';
import "./input.css";

class Login extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      active: props.active || false,
      password: props.password || "",
      email: props.email || ""
    };

    this.handleChange = this.handleChange.bind(this);
  }
  
  handleChange(event) {
    const target = event.target;
    const value = target.value;
    const name = target.name;

    console.log(`Input name ${name}. Input value ${value}.`);

    this.setState({
      [name]: value
    });
  }

  render() {
    const { active, email, password } = this.state;
    const fieldClassName = `field ${active ? 'active' : ''}`

    return (
      <div>
        Login<br /><br />
        
        <div className={fieldClassName}>
          <input
          name="email"
          type="text"
          label="email"
          value={this.state.email}
          active={false}
          onChange={this.handleChange}
          onFocus={() => this.setState({ active: true })}
          onBlur={() => this.setState({ active: false })}
          />
          <label htmlFor="email">
          email
          </label>
        </div>
        
        <div className={fieldClassName}>
          <input
          type="password"
          label="password"
          value={this.state.password}
          active={false}
          onChange={this.handleChange}
          onFocus={() => this.setState({ active: true })}
          onBlur={() => this.setState({ active: false })}
          />
          <label htmlFor="password">
          password
          </label>
        </div>
       </div>
    );
  }
}

export default Login;
