import React from "react";
import "./index.css";
import axios from 'axios';
import { getToken } from './utils/common';
import { Message, Container, Grid, Dropdown, Modal, Button, Icon, Input, Label, Card, Image  } from 'semantic-ui-react'
import { DateInput } from 'semantic-ui-calendar-react';
import _ from 'lodash'

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
      modalopen: false,
      itemaddedmsg: '',
      itemadded: false
    }
  }

  fetchinventory(){
    axios.get('http://127.0.0.1:8989/inventory?isedible=2&ispartiallyconsumed=2&sortby=productname',
      {
        headers: {
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        this.setState({ inventory: response.data[0]['results'] });
      }
    })
    .catch(error => {
      if(error.response){
        console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
      }
      else{
        console.log('fatal: server unreachable');
      }
    });
  }

  componentDidMount() {
    this.fetchinventory();
  }

  lookupproduct(event, data){
    const gtinorproduct = data.searchQuery

    if(gtinorproduct.length > 3){
      axios.get('http://127.0.0.1:8989/product/' + gtinorproduct + '?isedible=2',
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          this.updateproductsuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        }
        else{
          console.log('fatal: server unreachable');
        }
      });
    }
  }

  lookupretailer(event, data){
    const retailer = data.searchQuery

    if(retailer.length > 3){
      axios.get('http://127.0.0.1:8989/retailer/' + retailer,
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          this.updateretailersuggests(response.data[0]['results']);
        }
      })
      .catch(error => {
        if(error.response){
          console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        }
        else{
          console.log('fatal: server unreachable');
        }
      });
    }
  }

  lookupbrand(brand){
    if(brand.length > 3){
      axios.get('http://127.0.0.1:8989/brand/' + brand,
        {
          headers: {
            "content-type": "application/json",
            "access-token": this.state.token
          }
        }
      )
      .then(response => { 
        if(response.status === 200){
          this.setState({ brandsuggests: response.data[0]['results'] });
        }
      })
      .catch(error => {
        if(error.response){
          console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        }
        else{
          console.log('fatal: server unreachable');
        }
      });
    }
  }

  setinventorymetadata(event, data){
    const field = data.placeholder;
    const value = data.value;
    console.log(field + ':' + value);
    if(field === 'product'){
      const array = this.state.productsuggests;
      let selectedgtin = array.filter(prod => prod.value.includes(value))[0]['key'];

      this.setState({ tempgtin: selectedgtin });
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
    const { tempgtin, tempproductname, tempretailername, tempquantity, tempdateexpiry} = this.state;
  
    console.log("saving=>" + tempgtin + ':' + tempproductname + ':' + tempretailername + ':' + tempquantity + ':' + tempdateexpiry);

    axios.post('http://127.0.0.1:8989/inventory', 
      {
        gtin:tempgtin,
        retailername:tempretailername,
        dateexpiry:tempdateexpiry,
        quantity:tempquantity,
        itemstatus:'IN',
        receiptno:''
      }, 
      {
        headers: {
          'crossDomain': true,
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        this.setState({ itemaddedmsg: response.data[0]['message'] });
        this.setState({ itemadded: true });
        this.setState({ gtin: '' });
        this.setState({ retailername: ''});
        this.setState({ dateexpiry: ''});
        this.setState({ quantity: 1 });
      }
    })
    .catch(error => {
      if(error.response){
        console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        this.setState({ itemaddedmsg: error.response.data[0]['message'] });        
      }
      else{
        console.log('fatal: server unreachable');
        this.setState({ itemaddedmsg: 'fatal: server unreachable' });
      }
    });
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

  inventoryconsume(gtin){
    console.log(gtin);  
    axios.post('http://127.0.0.1:8989/inventory', 
      {
        gtin:gtin,
        retailername:'',
        dateexpiry:'',
        quantity:0.5,
        itemstatus:'OUT',
        receiptno:''
      }, 
      {
        headers: {
          'crossDomain': true,
          "content-type": "application/json",
          "access-token": this.state.token
        }
      }
    )
    .then(response => { 
      if(response.status === 200){
        console.log(response.data[0]['message']);
        this.setState({ inventory: response.data[0]['results'] });
      }
    })
    .catch(error => {
      if(error.response){
        console.log('(' + error.response.status + ') ' + error.response.data[0]['message']);
        //this.setState({ itemaddedmsg: error.response.data[0]['message'] });        
      }
      else{
        console.log('fatal: server unreachable');
        //this.setState({ itemaddedmsg: 'fatal: server unreachable' });
      }
    });    
  }
  
  openmodal = () => this.setState({ modalopen: true })
  closemodal = () => this.setState({ modalopen: false })

  generategriddefault(){
    let itemaddedstatus = '';
    if(this.state.itemaddedmsg !== ''){
      if(this.state.itemadded){
        itemaddedstatus = (
          <Message className="fullwidth" success><Message.Header>{this.state.itemaddedmsg}</Message.Header></Message>
        );
      }
      else{
        itemaddedstatus = (
          <Message className="fullwidth" negative><Message.Header>{this.state.itemaddedmsg}</Message.Header></Message>        
        );
      }
    }
    return (
      <Card raised key="1">
        <Card.Content>
          <Image rounded
            centered src="https://react.semantic-ui.com/images/wireframe/image.png"
            floated='right'
            size='tiny'
          />
          <Card.Header size='tiny'>Add new item</Card.Header>
          <Card.Meta></Card.Meta>
          <Label color='grey' attached='top right'>0</Label>
        </Card.Content>

        <Card.Content extra textAlign="center">
          <Modal
            trigger={<Button icon="plus" onClick={this.openmodal} />}
            open={this.state.modalopen}
            onClose={this.closemodal} 
            centered={false}
            size="fullscreen"
            dimmer="blurring"
            >
            <Modal.Header>add item into inventory</Modal.Header>
            <Modal.Content>
              <Grid columns={1} doubling stackable>
                <Grid.Column>
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
                </Grid.Column>
                <Grid.Column>
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
                </Grid.Column>
                <Grid.Row columns={2}>
                  <Grid.Column>
                    <Input className="fullwidth"
                      placeholder='quantity'
                      value={this.state.tempquantity}
                      onChange={this.setinventorymetadata.bind(this)}
                    />
                  </Grid.Column>
                  <Grid.Column>
                     <DateInput className="fullwidth"
                      placeholder="expiry"
                      dateFormat="YYYY-MM-DD"
                      value={this.state.tempdateexpiry}
                      onChange={this.setinventorymetadata.bind(this)}
                    />
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Modal.Content>
            <Modal.Actions>
              <Grid columns={2} container doubling stackable>
                <Grid.Column>
                  <Button className="fullwidth" color='black' onClick={this.addinventory.bind(this)}>
                    <Icon name='checkmark' />save
                  </Button>
                </Grid.Column>
                <Grid.Column>
                  {itemaddedstatus}
                </Grid.Column>
              </Grid>
            </Modal.Actions>
          </Modal>
        </Card.Content>
      </Card>
    )
  }
  generategriditems(){
    return _.map(this.state.inventory, (item) => (
            <Card raised key={item.gtin}>
              <Card.Content>
                <Image rounded
                  centered src={item.productimage}
                  floated='right'
                  size='tiny'
                />
                <Card.Header size='tiny'>{item.productname}</Card.Header>
                <Card.Meta>{item.brandname}</Card.Meta>
                <Label color='grey' attached='top right'>{item.itemcount}</Label>
              </Card.Content>

              <Card.Content extra textAlign="center">
                <div className='ui three buttons'>
                  <Modal
                    trigger={<Button icon="edit" />}
                    centered={false}
                    basic
                    size="fullscreen"
                    dimmer="blurring"
                  >
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
                  <Button icon="minus" onClick={this.inventoryconsume.bind(this,item.gtin)}/>
                  <Button icon="plus" />
                </div>
              </Card.Content>
            </Card>
          ))
  }

  render() {
    return (
      <Container fluid>
        <Card.Group doubling itemsPerRow={6} stackable>
          {this.generategriddefault()}
          {this.generategriditems()}
        </Card.Group>
      </Container>
    )
  }
}
export default Inventory;
