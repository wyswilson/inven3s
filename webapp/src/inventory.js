import React, {Fragment} from "react";
import "./index.css";
import axios from 'axios';
import { getToken } from './utils/common';
import _ from 'lodash'
import { Dropdown, Modal, Button, Icon, Input, Label, Card, Image, Header  } from 'semantic-ui-react'
import { DateInput } from 'semantic-ui-calendar-react';

class Inventory extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      token: getToken(),
      gtin: '',
      productname: '',
      productimage: '',
      retailerid:'',
      retailername:'',
      inventory:[],
      productsuggests: [],
      retailersuggests: [],
      brandsuggests: [],
      tempgtin:'',
      tempproductname: '',
      tempproductimage: '',
      tempbrandid:'',
      tempbrandname: '',
      tempretailerid:'',
      tempretailername: '',
      tempquantity: 1,
      tempdateexpiry: '',
      modalopen: false
    }
  }

  fetchinventory(){
    const { token } = this.state;
    
    if (!token) {
      return;
    }

    axios.get('http://127.0.0.1:8989/inventory',
      { headers: { "content-type": "application/json", "access-token": token } }
    )
    .then(response => { 
      if(response.status === 200){
        const inventoryitems = response.data[0]['results'];
        this.setState({ inventory:inventoryitems });
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

  componentDidMount() {
    this.fetchinventory();
  }

  lookupproduct(event, data){
    const { token } = this.state;
    const gtinorproduct = data.searchQuery

    if(gtinorproduct.length > 3){
      axios.get('http://127.0.0.1:8989/product/' + gtinorproduct,
        { headers: { "content-type": "application/json", "access-token": token } }
      )
      .then(response => { 
        if(response.status === 200){
          const suggestions = response.data[0]['results'];
          this.updateproductsuggests(suggestions);
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
  }

  lookupretailer(event, data){
    const { token } = this.state;
    const retailer = data.searchQuery

    if(retailer.length > 3){
      axios.get('http://127.0.0.1:8989/retailer/' + retailer,
        { headers: { "content-type": "application/json", "access-token": token } }
      )
      .then(response => { 
        if(response.status === 200){
          const suggestions = response.data[0]['results'];
          this.updateretailersuggests(suggestions);
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
  }

  lookupbrand(brand){
    const { token } = this.state;

    if(brand.length > 3){
      axios.get('http://127.0.0.1:8989/brand/' + brand,
        { headers: { "content-type": "application/json", "access-token": token } }
      )
      .then(response => { 
        if(response.status === 200){
          const suggestions = response.data[0]['results'];
          this.setState({ brandsuggests:suggestions });
          console.log(suggestions);
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
  }

  setinventorymetadata(event, data){
    const field = data.placeholder;
    const value = data.value;
    console.log(field + ':' + value);
    if(field === 'product'){
      this.setState({ tempproductname: value });
    }
    else if(field === 'retailer'){
      this.setState({ tempretailername: value });
    }
    else if(field === 'quantity'){
      this.setState({ tempquantity: value });
    }
    else if(field === 'expiry'){
      this.setState({ tempdateexpiry: value });
    }
  }
  
  addinventory(event){
    const { tempproductname, tempretailername, tempquantity, tempdateexpiry} = this.state;
  
    console.log("saving=>" + tempproductname + ':' + tempretailername + ':' + tempquantity + ':' + tempdateexpiry);
  }

  updateproductsuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.gtin,
          text: item.productname,
          value: item.productname,
        }
      ));
    console.log(updatedsuggest);
    this.setState({ productsuggests: updatedsuggest });
  }

  updateretailersuggests(suggestions){
    const updatedsuggest = _.map(suggestions, (item) => (
        {
          key: item.retailerid,
          text: item.retailername,
          value: item.retailername,
        }
      ));
    console.log(updatedsuggest);
    this.setState({ retailersuggests: updatedsuggest });
  }

  addnewproduct(event,data){
    console.log(data.value);
  }

  addnewretailer(event,data){
    console.log(data.value);
  }

  openmodal = () => this.setState({ modalopen: true })

  closemodal = () => this.setState({ modalopen: false })

  render() {
    const griditems = _.map(this.state.inventory, (item) => (
            <Card raised key={item.gtin}>
              <Image rounded centered src={item.productimage} size="tiny"/>
              <Card.Content>
                <Label color='grey' ribbon>{item.itemcount}</Label>
                <Fragment>
                  <Card.Description className="cardy">
                    <Header size='tiny'>{item.productname}</Header>
                  </Card.Description>
                  <Card.Meta>{item.brandname}</Card.Meta>
                </Fragment>
              </Card.Content>

              <Card.Content extra textAlign="center">
                <Modal trigger={<Button icon="edit" />} centered>
                  <Modal.Header>edit product and brand</Modal.Header>
                  <Modal.Content image>
                    <Image wrapped size='medium' src={item.productimage} />
                    <Modal.Description>
                      {item.productname}
                      <Input className="fullwidth" onChange={e => this.setState({ tempgtin:item.gtin, tempproductname: e.target.value })}/>
                      {item.productimage}
                      <Input className="fullwidth" onChange={e => this.setState({ tempgtin:item.gtin, tempproductimage: e.target.value })}/>
                      {item.brandname}
                      
                      <Button color="black">save</Button>
                    </Modal.Description>
                  </Modal.Content>
                </Modal>
                <Button icon="minus" />
                <Button icon="plus" />
              </Card.Content>
            </Card>
          ))

    return (
      <div>
         
        <Card.Group doubling itemsPerRow={6} stackable>
          <Card raised key="1">
            <Image rounded centered src="https://react.semantic-ui.com/images/wireframe/image.png" size="tiny"/>
            <Card.Content>
              <Label color='grey' ribbon>0</Label>
              <Fragment>
                <Card.Meta>
                  
                </Card.Meta>
              </Fragment>
            </Card.Content>

            <Card.Content extra textAlign="center">
              <Modal
                trigger={<Button icon="plus" onClick={this.openmodal} />}
                open={this.state.modalopen}
                onClose={this.closemodal} centered
              >
                <Modal.Header>add item into inventory</Modal.Header>
                <Modal.Content>
                  <Dropdown className="fullwidth"
                    placeholder="product"
                    search
                    selection
                    allowAdditions
                    value={this.state.tempproductname}
                    options={this.state.productsuggests}
                    additionLabel = "add new product "
                    onSearchChange={this.lookupproduct.bind(this)}
                    onAddItem={this.addnewproduct.bind(this)}
                    onChange={this.setinventorymetadata.bind(this)}
                  />
                  <Dropdown className="fullwidth"
                    placeholder="retailer"
                    search
                    selection
                    allowAdditions
                    value={this.state.tempretailername}
                    options={this.state.retailersuggests}
                    additionLabel = "add new retailer "
                    onSearchChange={this.lookupretailer.bind(this)}
                    onAddItem={this.addnewretailer.bind(this)}
                    onChange={this.setinventorymetadata.bind(this)}
                  />
                  <Input className="fullwidth"
                    placeholder='quantity'
                    value={this.state.tempquantity}
                    onChange={this.setinventorymetadata.bind(this)}
                  />
                   <DateInput className="fullwidth"
                    placeholder="expiry"
                    dateFormat="YYYY-MM-DD"
                    value={this.state.tempdateexpiry}
                    onChange={this.setinventorymetadata.bind(this)}
                  />

                </Modal.Content>
                <Modal.Actions>
                  <Button color='black' onClick={this.addinventory.bind(this)}>
                    <Icon name='checkmark' />save
                  </Button>
                </Modal.Actions>
              </Modal>
            </Card.Content>
          </Card>
          {griditems}
        </Card.Group>
      </div>
    )
  }
}
export default Inventory;
