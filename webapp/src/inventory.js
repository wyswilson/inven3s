import React from 'react';
import Input from './input.js';
import "./field.css";

function Inventory(props) {
  return (
    <div>
      <form>
      
      <Input
        id={1}
        type="text"
        label="GTIN"
        predicted=""
        locked={false}
        active={false}
      />

      <Input
        id={2}
        type="text"
        label="Retailer"
        predicted=""
        locked={false}
        active={false}
      />

    </form>
    </div>
     
  );
}

export default Inventory;
