import React from 'react';
import Input from './input.js';

function Inventory(props) {

  return (
    <div>
      <form>
      <div>
        <Input
          id={1}
          type="text"
          label="GTIN"
          predicted=""
          locked={false}
          active={false}
        />
      </div>
      <div style={{ marginTop: 10 }}>
        <Input
          id={2}
          type="text"
          label="Retailer"
          predicted=""
          locked={false}
          active={false}
        />
      </div>
    </form>
    </div>
     
  );
}

export default Inventory;
