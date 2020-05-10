import React from "react";
import Field from './field.js';
import { Button, Message } from 'semantic-ui-react'
import axios from 'axios';
import { getToken } from './utils/common';
import './field.css';
import './index.css';

class Inventory extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      token: getToken(),
      gtin: '',
      productname: ''
    }
  }
  
  lookupproduct(gtin){
    const { token } = this.state;
    this.setState({ gtin:gtin });
    this.setState({ productname:'' });

    axios.get('http://127.0.0.1:8989/product/' + gtin,
      { headers: { "content-type": "application/json", "access-token": token } }
    )
    .then(response => { 
      if(response.status === 200){
        const productname = response.data[0]['results'][0]['productname'];
        console.log(productname);
        this.setState({ productname:productname });
      }
    })
    .catch(error => {
      const errresponse = error.response
      if(errresponse){
        if(errresponse.status === 412){
          const message = errresponse.data[0]['message'];
          console.log(message);
        }
        else{
          console.log(errresponse);
        }
      }
      else{
        console.log('internal server error');
      }
    });
  }
  updateinventory(field,value) {
    console.log('parent:'+field + ':' + value);

    if(field === 'gtin'){
      this.lookupproduct(value);
    }
    else if(field === 'retailer'){

    }
  }
  
  render() {
    const { token, gtin, productname } = this.state;

    return (
      <div>
      <Field label="gtin" type="text" active={false}
        parentCallback={this.updateinventory.bind(this)}/>
      {productname}
      <Field label="retailer" type="text" active={false}
        parentCallback={this.updateinventory.bind(this)}/>
      </div>
    )
  }
}
export default Inventory;
