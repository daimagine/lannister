DB changes :

- Update `product` table
```
-- Column: is_affiliate_ready
	-- ALTER TABLE product DROP COLUMN is_affiliate_ready;
	ALTER TABLE product ADD COLUMN is_affiliate_ready boolean;
	ALTER TABLE product ALTER COLUMN is_affiliate_ready SET DEFAULT false;
	update product set is_affiliate_ready = false;
	ALTER TABLE product ADD COLUMN affiliate_percentage numeric(3,2);
	ALTER TABLE product ADD COLUMN affiliate_fee numeric(12,2);
	ALTER TABLE product ADD COLUMN affiliate_fee_type character varying(1);
	```

- Create `affiliate` table
```
CREATE TABLE affiliate
(
  id bigint NOT NULL,
    customer_id bigint NOT NULL,
	  product__id bigint NOT NULL,
	    headline character varying(1024),
		  product_page character varying(1024),
		    CONSTRAINT pk_affiliate_id PRIMARY KEY (id),
			  CONSTRAINT fk_affiliate_customer_id FOREIGN KEY (customer_id)
			        REFERENCES customer (id) MATCH SIMPLE
					      ON UPDATE NO ACTION ON DELETE NO ACTION,
						    CONSTRAINT fk_affiliate_product_id FOREIGN KEY (product_id)
							      REFERENCES product (id) MATCH SIMPLE
								        ON UPDATE NO ACTION ON DELETE NO ACTION
										)
										WITH (
										  OIDS=FALSE
										  );
										  ALTER TABLE affiliate
										    OWNER TO postgres;
											```

- Add `affiliate sequence`
```
CREATE SEQUENCE seq_affiliate_id
  INCREMENT 1
    MINVALUE 1
	  MAXVALUE 9223372036854775807
	    START 1
		  CACHE 1;
		  ALTER TABLE seq_affiliate_id
		    OWNER TO postgres;
			```

- Update `social_media`
```
ALTER TABLE social_media ADD COLUMN plugin_package character varying(200);
```
