import React, { useState } from 'react';
import styled from 'styled-components/native';
import TextField from '../atoms/TextInput';
import Button from '../atoms/Button';

const Form = styled.View`
  width: 100%;
`;

export const LoginForm = ({ onSubmit, loading }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});

  const handlePress = () => {
    const nextErrors = {};
    if (!email.includes('@')) {
      nextErrors.email = 'Valid email required';
    }
    if (password.length < 8) {
      nextErrors.password = 'Password must be at least 8 characters';
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length === 0) {
      onSubmit({ email, password });
    }
  };

  return (
    <Form>
      <TextField
        label="Email"
        keyboardType="email-address"
        autoCapitalize="none"
        value={email}
        onChangeText={setEmail}
        error={errors.email}
      />
      <TextField
        label="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        error={errors.password}
      />
      <Button title="Sign In" onPress={handlePress} loading={loading} />
    </Form>
  );
};

export default LoginForm;
