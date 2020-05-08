import React from "react";
import Field from './field.js';

class Inventory extends React.Component {
  constructor(props) {
    super(props)
  }
  
  handleChange(e) {
    e.preventDefault()
  }
  
  render() {
    return (
      <div>
        <Field label="gtin" type="text" active={false} />
        <Field label="retailer" type="text" active={false} />
        <div></div>
      </div>
    )
  }
}
export default Inventory;
