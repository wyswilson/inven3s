import React, {Fragment} from "react";
import "./index.css";
import { Search } from 'semantic-ui-react'
import axios from 'axios';
import { getToken } from './utils/common';
import PropTypes from 'prop-types'
import _ from 'lodash'
import { Dropdown, Modal, Button, Icon, Input, Label, Card, Image, Header  } from 'semantic-ui-react'

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
      modalOpen: false
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
        console.log(inventoryitems);
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

  updateinventory(field,value) {
    console.log('parent:'+field + ':' + value);

    if(field === 'gtin'){
      this.lookupproduct(value);
    }
    else if(field === 'retailer'){

    }
  }

  updateproductmetadata(event, data){
    console.log(data);
    //const { tempgtin, tempproductname, tempproductimage, tempbrandname } = this.state;
    //console.log('update with=>' + tempgtin + ':' + tempproductname + ':' + tempproductimage + ':' + tempbrandname);
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

  updatebrandsuggests(event){
    const brandname = event.target.value;
    this.lookupbrand(brandname);
  }

  selectproduct(event, { result }){
    if(result.gtin !== 'new-entry'){
      console.log("selected=>" + result.gtin + ":" + result.productname);
      this.setState({ gtin: result.gtin, productname: result.productname });
    }
    else{
      console.log('new-entry');
    }
  }

  selectbrand(event, { result }){
    if(result.brandid !== 'new-entry'){
      console.log("selected=>" + result.brandid + ":" + result.brandname);
      this.setState({ tempbrandid: result.brandid, tempbrandname: result.brandname });
    }
    else{
      console.log('new-entry');
    }
  }

  selectretailer(event, { result }){
    if(result.retailerid !== 'new-entry'){
      console.log("selected=>" + result.retailerid + ":" + result.retailername);
      this.setState({ retailerid: result.retailerid, retailername: result.retailername });
    }
    else{
      console.log('new-entry');
    }
  }

  handleOpen = () => this.setState({ modalOpen: true })

  handleClose = () => this.setState({ modalOpen: false })

  render() {
    const { gtin, productname, productimage, productsuggests, retailersuggests, brandsuggests, inventory } = this.state;
    const griditems = _.map(inventory, (item) => (
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
                      
                      <Button color="black" onClick={this.updateproductmetadata.bind(this)}>save</Button>
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
                trigger={<Button icon="plus" onClick={this.handleOpen} />}
                open={this.state.modalOpen}
                onClose={this.handleClose} centered
              >
                <Modal.Header>add item into inventory</Modal.Header>
                <Modal.Content>
                  <Dropdown className="fullwidth"
                    text="product"
                    search
                    selection
                    allowAdditions
                    options={productsuggests}
                    searchQuery={}
                    additionLabel = "add new product "
                    onSearchChange={this.lookupproduct.bind(this)}
                    onAddItem={this.addnewproduct.bind(this)}
                    onClick={this.updateproductmetadata.bind(this)}
                  />
                  
                  <Dropdown className="fullwidth"
                    text="retailer"
                    search
                    selection
                    allowAdditions
                    options={retailersuggests}
                    additionLabel = "add new retailer "
                    onSearchChange={this.lookupretailer.bind(this)}
                    onAddItem={this.addnewretailer.bind(this)}
                  />
                  <Input placeholder='quantity'
                  />
                </Modal.Content>
                <Modal.Actions>
                  <Button color='green' onClick={this.handleClose} inverted>
                    <Icon name='checkmark' /> Got it
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
